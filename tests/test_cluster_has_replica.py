from click.testing import CliRunner
from pytest_mock import MockerFixture

from check_patroni.cli import main

from .tools import my_mock


# TODO Lag threshold tests
def test_cluster_has_relica_ok(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ok", 200, use_old_replica_state)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_replica"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERHASREPLICA OK - healthy_replica is 2 | healthy_replica=2 srv2_lag=0 srv2_sync=0 srv3_lag=0 srv3_sync=1 sync_replica=1 unhealthy_replica=0\n"
    )


def test_cluster_has_replica_ok_with_count_thresholds(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ok", 200, use_old_replica_state)
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
    assert (
        result.stdout
        == "CLUSTERHASREPLICA OK - healthy_replica is 2 | healthy_replica=2;@1;@0 srv2_lag=0 srv2_sync=0 srv3_lag=0 srv3_sync=1 sync_replica=1 unhealthy_replica=0\n"
    )


def test_cluster_has_replica_ok_with_sync_count_thresholds(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ok", 200, use_old_replica_state)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_has_replica",
            "--sync-warning",
            "1:",
        ],
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERHASREPLICA OK - healthy_replica is 2 | healthy_replica=2 srv2_lag=0 srv2_sync=0 srv3_lag=0 srv3_sync=1 sync_replica=1;1: unhealthy_replica=0\n"
    )


def test_cluster_has_replica_ok_with_count_thresholds_lag(
    mocker: MockerFixture,
    use_old_replica_state: bool,
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ok_lag", 200, use_old_replica_state)
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
    assert (
        result.stdout
        == "CLUSTERHASREPLICA OK - healthy_replica is 2 | healthy_replica=2;@1;@0 srv2_lag=1024 srv2_sync=0 srv3_lag=0 srv3_sync=0 sync_replica=0 unhealthy_replica=0\n"
    )


def test_cluster_has_replica_ko_with_count_thresholds(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ko", 200, use_old_replica_state)
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
    assert (
        result.stdout
        == "CLUSTERHASREPLICA WARNING - healthy_replica is 1 (outside range @0:1) | healthy_replica=1;@1;@0 srv3_lag=0 srv3_sync=0 sync_replica=0 unhealthy_replica=1\n"
    )


def test_cluster_has_replica_ko_with_sync_count_thresholds(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ko", 200, use_old_replica_state)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_has_replica",
            "--sync-warning",
            "2:",
            "--sync-critical",
            "1:",
        ],
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "CLUSTERHASREPLICA CRITICAL - sync_replica is 0 (outside range 1:) | healthy_replica=1 srv3_lag=0 srv3_sync=0 sync_replica=0;2:;1: unhealthy_replica=1\n"
    )


def test_cluster_has_replica_ko_with_count_thresholds_and_lag(
    mocker: MockerFixture,
    use_old_replica_state: bool,
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ko_lag", 200, use_old_replica_state)
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
    assert (
        result.stdout
        == "CLUSTERHASREPLICA CRITICAL - healthy_replica is 0 (outside range @0:0) | healthy_replica=0;@1;@0 srv2_lag=10241024 srv2_sync=0 srv3_lag=20000000 srv3_sync=0 sync_replica=0 unhealthy_replica=2\n"
    )
