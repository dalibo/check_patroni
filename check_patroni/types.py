import logging

import attr
import nagiosplugin
import requests
import urllib3
from typing import Any, Callable, List, Optional, Tuple, Union

_log = logging.getLogger("nagiosplugin")


class APIError(requests.exceptions.RequestException):
    """This exception is raised when the rest api couldn't
    be reached and we got a http status code different from 200.
    """


@attr.s(auto_attribs=True, frozen=True, slots=True)
class ConnectionInfo:
    endpoints: List[str] = ["http://127.0.0.1:8008"]
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_cert: Optional[str] = None


@attr.s(auto_attribs=True, frozen=True, slots=True)
class Parameters:
    connection_info: ConnectionInfo
    timeout: int
    verbose: int


@attr.s(auto_attribs=True, slots=True)
class PatroniResource(nagiosplugin.Resource):
    conn_info: ConnectionInfo

    def rest_api(self: "PatroniResource", service: str) -> Any:
        """Try to connect to all the provided endpoints for the requested service"""
        for endpoint in self.conn_info.endpoints:
            try:
                cert: Optional[Union[Tuple[str, str], str]] = None
                verify: Optional[Union[str, bool]] = None
                if endpoint[:5] == "https":
                    if (
                        self.conn_info.cert_file is not None
                        and self.conn_info.key_file is not None  # noqa W503
                    ):
                        # we provide a certificate and a private key
                        cert = (self.conn_info.cert_file, self.conn_info.key_file)
                    elif (
                        self.conn_info.cert_file is not None
                        and self.conn_info.key_file is None  # noqa W503
                    ):
                        # we provide a pem file with the private key and the certificate
                        cert = self.conn_info.cert_file

                    if self.conn_info.ca_cert is not None:
                        # if cert is not None: this is the CA certificate
                        # otherwise this is a ca bundle with root certificate
                        # then some optional intermediate certificate and finally
                        # the cerver certificate to validate the certification chain
                        verify = self.conn_info.ca_cert
                    else:
                        if cert is None:
                            # if cert is None we want to bypass https verification,
                            # this is in secure and should be avoided for production use
                            verify = False

                _log.debug(
                    f"Trying to connect to {endpoint}/{service} with cert: {cert} verify: {verify}"
                )

                r = requests.get(f"{endpoint}/{service}", verify=verify, cert=cert)
                _log.debug(f"api call status: {r.status_code}")
                _log.debug(f"api call data: {r.text}")

                if r.status_code != 200:
                    raise APIError(
                        f"Failed to connect to {endpoint}/{service} status code {r.status_code}"
                    )

                return r.json()
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
