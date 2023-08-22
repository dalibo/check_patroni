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


def my_mock(
    mocker: MockerFixture,
    json_file: str,
    status: int,
    use_old_replica_state: bool = False,
) -> None:
    def mock_rest_api(self: PatroniResource, service: str) -> Any:
        if status != 200:
            raise APIError("Test en erreur pour status code 200")
        if json_file:
            if use_old_replica_state and (
                json_file.startswith("cluster_has_replica")
                or json_file.startswith("cluster_node_count")
            ):
                return cluster_api_set_replica_running(getjson(json_file))
            return getjson(json_file)
        return None

    mocker.resetall()
    mocker.patch("check_patroni.types.PatroniResource.rest_api", mock_rest_api)


def cluster_api_set_replica_running(js: Any) -> Any:
    # starting from 3.0.4 the state of replicas is streaming instead of running
    for node in js["members"]:
        if node["role"] in ["replica", "sync_standby"]:
            if node["state"] == "streaming":
                node["state"] = "running"
    return js
