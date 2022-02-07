from pytest_mock import MockerFixture

from click.testing import CliRunner

from check_patroni.cli import main
from tools import my_mock


def test_cluster_is_in_maintenance_ok(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_is_in_maintenance_ok", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_is_in_maintenance"]
    )
    assert result.exit_code == 0


def test_cluster_is_in_maintenance_ko(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_is_in_maintenance_ko", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_is_in_maintenance"]
    )
    assert result.exit_code == 2


def test_cluster_is_in_maintenance_ok_pause_false(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_is_in_maintenance_ok_pause_false", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_is_in_maintenance"]
    )
    assert result.exit_code == 0
