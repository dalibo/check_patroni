from click.testing import CliRunner
from pytest_mock import MockerFixture

from check_patroni.cli import main

from .tools import my_mock


def test_cluster_is_in_maintenance_ok(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_is_in_maintenance_ok", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_is_in_maintenance"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERISINMAINTENANCE OK - is_in_maintenance is 0 | is_in_maintenance=0;;0\n"
    )


def test_cluster_is_in_maintenance_ko(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_is_in_maintenance_ko", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_is_in_maintenance"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "CLUSTERISINMAINTENANCE CRITICAL - is_in_maintenance is 1 (outside range 0:0) | is_in_maintenance=1;;0\n"
    )


def test_cluster_is_in_maintenance_ok_pause_false(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_is_in_maintenance_ok_pause_false", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_is_in_maintenance"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERISINMAINTENANCE OK - is_in_maintenance is 0 | is_in_maintenance=0;;0\n"
    )
