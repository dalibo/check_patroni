import attr
import pathlib
from pytest_mock import MockerFixture

from check_patroni.types import PatroniResource

here = pathlib.Path(__file__).parent


def getjson(name: str) -> bytes:
    path = here / "json" / f"{name}.json"
    with path.open() as f:
        return f.read().encode("utf-8")


@attr.s(auto_attribs=True, frozen=True, slots=True)
class MockApiReturnCode:
    data: bytes
    status: int


def my_mock(mocker: MockerFixture, json_file: str, status: int) -> None:
    def mock_rest_api(self: PatroniResource, service: str) -> MockApiReturnCode:
        return MockApiReturnCode(getjson(json_file), status)

    mocker.patch("check_patroni.types.PatroniResource.rest_api", mock_rest_api)
