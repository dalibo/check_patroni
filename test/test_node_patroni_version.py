from pytest_mock import MockerFixture

from click.testing import CliRunner

from check_patroni.cli import main
from tools import my_mock


def test_node_patroni_version_ok(mocker: MockerFixture) -> None:
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


def test_node_patroni_version_ko(mocker: MockerFixture) -> None:
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
