from click.testing import CliRunner
from pytest_mock import MockerFixture

from check_patroni.cli import main

from .tools import my_mock


def test_node_is_pending_restart_ok(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_is_pending_restart_ok", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_pending_restart"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISPENDINGRESTART OK - This node doesn't have the pending restart flag. | is_pending_restart=0;;0\n"
    )


def test_node_is_pending_restart_ko(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_is_pending_restart_ko", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_pending_restart"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISPENDINGRESTART CRITICAL - This node has the pending restart flag. | is_pending_restart=1;;0\n"
    )
