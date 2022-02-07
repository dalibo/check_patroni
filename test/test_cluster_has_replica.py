from pytest_mock import MockerFixture

from click.testing import CliRunner

from check_patroni.cli import main
from tools import my_mock


# TODO Lag threshold tests
def test_cluster_has_relica_ok(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ok", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_replica"]
    )
    assert result.exit_code == 0


def test_cluster_has_replica_ok_with_count_thresholds(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ok", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_has_replica",
            "--warning",
            "@1",
            "--critical",
            "@0",
        ],
    )
    assert result.exit_code == 0


def test_cluster_has_replica_ok_with_count_thresholds_lag(
    mocker: MockerFixture,
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ok_lag", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_has_replica",
            "--warning",
            "@1",
            "--critical",
            "@0",
            "--max-lag",
            "1MB",
        ],
    )
    assert result.exit_code == 0


def test_cluster_has_replica_ko_with_count_thresholds(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ko", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_has_replica",
            "--warning",
            "@1",
            "--critical",
            "@0",
        ],
    )
    assert result.exit_code == 1


def test_cluster_has_replica_ko_with_count_thresholds_and_lag(
    mocker: MockerFixture,
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ko_lag", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_has_replica",
            "--warning",
            "@1",
            "--critical",
            "@0",
            "--max-lag",
            "1MB",
        ],
    )
    assert result.exit_code == 2
