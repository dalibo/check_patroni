import json
import pathlib
from typing import Any

from pytest_mock import MockerFixture

from check_patroni.types import APIError, PatroniResource

here = pathlib.Path(__file__).parent


def getjson(name: str) -> Any:
    path = here / "json" / f"{name}.json"
    if not path.exists():
        raise Exception(f"path does not exist : {path}")

    with path.open() as f:
        return json.load(f)


def my_mock(mocker: MockerFixture, json_file: str, status: int) -> None:
    def mock_rest_api(self: PatroniResource, service: str) -> Any:
        if status != 200:
            raise APIError("Test en erreur pour status code 200")
        return getjson(json_file)

    mocker.resetall()
    mocker.patch("check_patroni.types.PatroniResource.rest_api", mock_rest_api)
