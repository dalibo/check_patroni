from click.testing import CliRunner
from pytest_mock import MockerFixture

from check_patroni.cli import main

from .tools import my_mock


def test_node_is_primary_ok(mocker: MockerFixture, use_old_replica_state: bool) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_is_primary_ok", 200)
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_primary"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISPRIMARY OK - This node is the primary with the leader lock. | is_primary=1;;@0\n"
    )


def test_node_is_primary_ko(mocker: MockerFixture, use_old_replica_state: bool) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_is_primary_ko", 503)
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_primary"])
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISPRIMARY CRITICAL - This node is not the primary with the leader lock. | is_primary=0;;@0\n"
    )
