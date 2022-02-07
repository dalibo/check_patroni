from pytest_mock import MockerFixture

from click.testing import CliRunner

from check_patroni.cli import main
from tools import my_mock


def test_node_is_replica_ok(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_is_replica_ok", 200)
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_replica"])
    assert result.exit_code == 0


def test_node_is_replica_ko(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_is_replica_ko", 404)
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_replica"])
    assert result.exit_code == 2


def test_node_is_replica_ko_lag(mocker: MockerFixture) -> None:
    runner = CliRunner()

    # We don't do the check ourselves, patroni does it and changes the return code
    my_mock(mocker, "node_is_replica_ok", 404)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_replica", "--max-lag", "100"]
    )
    assert result.exit_code == 2
