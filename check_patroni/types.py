import json
from functools import lru_cache
from typing import Any, Callable, List, Optional, Tuple, Union
from urllib.parse import urlparse

import attr
import nagiosplugin
import requests

from . import _log


class APIError(requests.exceptions.RequestException):
    """This exception is raised when the rest api couldn't
    be reached and we got a http status code different from 200.
    """


@attr.s(auto_attribs=True, frozen=True, slots=True)
class ConnectionInfo:
    endpoints: List[str] = ["http://127.0.0.1:8008"]
    cert: Optional[Union[str, Tuple[str, str]]] = None
    ca_cert: Optional[str] = None


@attr.s(auto_attribs=True, frozen=True, slots=True)
class Parameters:
    connection_info: ConnectionInfo
    timeout: int
    verbose: int


@attr.s(auto_attribs=True, eq=False, slots=True)
class PatroniResource(nagiosplugin.Resource):
    conn_info: ConnectionInfo

    def rest_api(self, service: str) -> Any:
        """Try to connect to all the provided endpoints for the requested service"""
        for endpoint in self.conn_info.endpoints:
            cert: Optional[Union[Tuple[str, str], str]] = None
            verify: Optional[Union[str, bool]] = None
            if urlparse(endpoint).scheme == "https":
                if self.conn_info.cert is not None:
                    # we can have: a key + a cert or a single file with key and cert.
                    cert = self.conn_info.cert
                if self.conn_info.ca_cert is not None:
                    verify = self.conn_info.ca_cert

            _log.debug(
                "Trying to connect to %(endpoint)s/%(service)s with cert: %(cert)s verify: %(verify)s",
                {
                    "endpoint": endpoint,
                    "service": service,
                    "cert": cert,
                    "verify": verify,
                },
            )

            try:
                r = requests.get(f"{endpoint}/{service}", verify=verify, cert=cert)
            except Exception as e:
                _log.debug(e)
                continue
            # The status code is already displayed by urllib3
            _log.debug(
                "api call data: %(data)s", {"data": r.text if r.text else "<Empty>"}
            )

            if r.status_code != 200:
                raise APIError(
                    f"Failed to connect to {endpoint}/{service} status code {r.status_code}"
                )

            try:
                return r.json()
            except (json.JSONDecodeError, ValueError):
                return None
        raise nagiosplugin.CheckError("Connection failed for all provided endpoints")

    @lru_cache(maxsize=None)
    def has_detailed_states(self) -> bool:
        # get patroni's version to find out if the "streaming" and "in archive recovery" states are available
        patroni_item_dict = self.rest_api("patroni")

        if tuple(
            int(v) for v in patroni_item_dict["patroni"]["version"].split(".", 2)
        ) >= (3, 0, 4):
            _log.debug(
                "Patroni's version is %(version)s, more detailed states can be used to check for the health of replicas.",
                {"version": patroni_item_dict["patroni"]["version"]},
            )

            return True

        _log.debug(
            "Patroni's version is %(version)s, the running state and the timelines must be used to check for the health of replicas.",
            {"version": patroni_item_dict["patroni"]["version"]},
        )
        return False


HandleUnknown = Callable[[nagiosplugin.Summary, nagiosplugin.Results], Any]


def handle_unknown(func: HandleUnknown) -> HandleUnknown:
    """decorator to handle the unknown state in Summary.problem"""

    def wrapper(summary: nagiosplugin.Summary, results: nagiosplugin.Results) -> Any:
        if results.most_significant[0].state.code == 3:
            """get the appropriate message for all unknown error"""
            return results.most_significant[0].hint
        return func(summary, results)

    return wrapper
