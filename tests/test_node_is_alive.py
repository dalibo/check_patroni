from click.testing import CliRunner
from pytest_mock import MockerFixture

from check_patroni.cli import main

from .tools import my_mock


def test_node_is_alive_ok(mocker: MockerFixture, use_old_replica_state: bool) -> None:
    runner = CliRunner()

    my_mock(mocker, None, 200)
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_alive"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISALIVE OK - This node is alive (patroni is running). | is_alive=1;;@0\n"
    )


def test_node_is_alive_ko(mocker: MockerFixture, use_old_replica_state: bool) -> None:
    runner = CliRunner()

    my_mock(mocker, None, 404)
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_alive"])
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISALIVE CRITICAL - This node is not alive (patroni is not running). | is_alive=0;;@0\n"
    )
