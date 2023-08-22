from click.testing import CliRunner
from pytest_mock import MockerFixture

from check_patroni.cli import main

from .tools import my_mock


def test_node_patroni_version_ok(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_patroni_version", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "node_patroni_version",
            "--patroni-version",
            "2.0.2",
        ],
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEPATRONIVERSION OK - Patroni's version is 2.0.2. | is_version_ok=1;;@0\n"
    )


def test_node_patroni_version_ko(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_patroni_version", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "node_patroni_version",
            "--patroni-version",
            "1.0.0",
        ],
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEPATRONIVERSION CRITICAL - Patroni's version is not 1.0.0. | is_version_ok=0;;@0\n"
    )
