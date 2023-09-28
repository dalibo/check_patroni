from typing import Iterator

import pytest
from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI


@pytest.fixture
def node_is_leader_ok(patroni_api: PatroniAPI) -> Iterator[None]:
    with patroni_api.routes(
        {
            "leader": "node_is_leader_ok.json",
            "standby-leader": "node_is_leader_ok_standby_leader.json",
        }
    ):
        yield None


@pytest.mark.usefixtures("node_is_leader_ok")
def test_node_is_leader_ok(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    result = runner.invoke(main, ["-e", patroni_api.endpoint, "node_is_leader"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISLEADER OK - This node is a leader node. | is_leader=1;;@0\n"
    )

    result = runner.invoke(
        main,
        ["-e", patroni_api.endpoint, "node_is_leader", "--is-standby-leader"],
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISLEADER OK - This node is a standby leader node. | is_leader=1;;@0\n"
    )


def test_node_is_leader_ko(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    result = runner.invoke(main, ["-e", patroni_api.endpoint, "node_is_leader"])
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISLEADER CRITICAL - This node is not a leader node. | is_leader=0;;@0\n"
    )

    result = runner.invoke(
        main,
        ["-e", patroni_api.endpoint, "node_is_leader", "--is-standby-leader"],
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISLEADER CRITICAL - This node is not a standby leader node. | is_leader=0;;@0\n"
    )
