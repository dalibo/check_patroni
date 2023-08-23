from click.testing import CliRunner
from pytest_mock import MockerFixture

from check_patroni.cli import main

from .tools import my_mock


def test_node_is_leader_ok(mocker: MockerFixture, use_old_replica_state: bool) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_is_leader_ok", 200)
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_leader"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISLEADER OK - This node is a leader node. | is_leader=1;;@0\n"
    )

    my_mock(mocker, "node_is_leader_ok_standby_leader", 200)
    result = runner.invoke(
        main,
        ["-e", "https://10.20.199.3:8008", "node_is_leader", "--is-standby-leader"],
    )
    print(result.stdout)
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISLEADER OK - This node is a standby leader node. | is_leader=1;;@0\n"
    )


def test_node_is_leader_ko(mocker: MockerFixture, use_old_replica_state: bool) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_is_leader_ko", 503)
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_leader"])
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISLEADER CRITICAL - This node is not a leader node. | is_leader=0;;@0\n"
    )

    my_mock(mocker, "node_is_leader_ko_standby_leader", 503)
    result = runner.invoke(
        main,
        ["-e", "https://10.20.199.3:8008", "node_is_leader", "--is-standby-leader"],
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISLEADER CRITICAL - This node is not a standby leader node. | is_leader=0;;@0\n"
    )
