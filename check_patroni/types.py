import logging
import urllib3

import attr
import nagiosplugin
from typing import Any, Callable, List

_log = logging.getLogger("nagiosplugin")


@attr.s(auto_attribs=True, frozen=True, slots=True)
class ConnectionInfo:
    endpoints: List[str] = ["http://127.0.0.1:8008"]
    cert_file: str = "./ssl/benoit-dalibo-cert.pem"
    key_file: str = "./ssl/benoit-dalibo-key.pem"
    ca_cert: str = "./ssl/CA-cert.pem"


@attr.s(auto_attribs=True, frozen=True, slots=True)
class Parameters:
    connection_info: ConnectionInfo
    timeout: int
    verbose: int


@attr.s(auto_attribs=True, slots=True)
class PatroniResource(nagiosplugin.Resource):
    conn_info: ConnectionInfo

    def rest_api(
        self: "PatroniResource", service: str
    ) -> urllib3.response.HTTPResponse:
        """Try to connect to all the provided endpoints for the requested service"""
        for endpoint in self.conn_info.endpoints:
            try:
                if endpoint[:5] == "https":
                    pool = urllib3.PoolManager(
                        cert_reqs="CERT_REQUIRED",
                        cert_file=self.conn_info.cert_file,
                        key_file=self.conn_info.key_file,
                        ca_certs=self.conn_info.ca_cert,
                    )
                else:
                    pool = urllib3.PoolManager()

                _log.debug(f"Trying to connect to {endpoint}/{service}")
                return pool.request(
                    "GET",
                    f"{endpoint}/{service}",
                )
            except nagiosplugin.Timeout as e:
                raise e
            except Exception as e:
                _log.debug(e)
                continue
        raise nagiosplugin.CheckError("Connection failed for all provided endpoints")


HandleUnknown = Callable[[nagiosplugin.Summary, nagiosplugin.Results], Any]


def handle_unknown(func: HandleUnknown) -> HandleUnknown:
    """decorator to handle the unknown state in Summary.problem"""

    def wrapper(summary: nagiosplugin.Summary, results: nagiosplugin.Results) -> Any:
        if results.most_significant[0].state.code == 3:
            """get the appropriate message for all unknown error"""
            return results.most_significant[0].hint
        return func(summary, results)

    return wrapper
