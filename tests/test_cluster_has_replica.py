from pathlib import Path
from typing import Iterator, Union

import pytest
from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI, cluster_api_set_replica_running


@pytest.fixture
def cluster_has_replica_ok(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_has_replica_ok.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_has_replica_ok")
def test_cluster_has_relica_ok(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    result = runner.invoke(main, ["-e", patroni_api.endpoint, "cluster_has_replica"])
    assert (
        result.stdout
        == "CLUSTERHASREPLICA OK - healthy_replica is 2 | healthy_replica=2 srv2_lag=0 srv2_sync=0 srv2_timeline=51 srv3_lag=0 srv3_sync=1 srv3_timeline=51 sync_replica=1 unhealthy_replica=0\n"
    )
    assert result.exit_code == 0


@pytest.mark.usefixtures("cluster_has_replica_ok")
def test_cluster_has_replica_ok_with_count_thresholds(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_has_replica",
            "--warning",
            "@1",
            "--critical",
            "@0",
        ],
    )
    assert (
        result.stdout
        == "CLUSTERHASREPLICA OK - healthy_replica is 2 | healthy_replica=2;@1;@0 srv2_lag=0 srv2_sync=0 srv2_timeline=51 srv3_lag=0 srv3_sync=1 srv3_timeline=51 sync_replica=1 unhealthy_replica=0\n"
    )
    assert result.exit_code == 0


@pytest.mark.usefixtures("cluster_has_replica_ok")
def test_cluster_has_replica_ok_with_sync_count_thresholds(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_has_replica",
            "--sync-warning",
            "1:",
        ],
    )
    assert (
        result.stdout
        == "CLUSTERHASREPLICA OK - healthy_replica is 2 | healthy_replica=2 srv2_lag=0 srv2_sync=0 srv2_timeline=51 srv3_lag=0 srv3_sync=1 srv3_timeline=51 sync_replica=1;1: unhealthy_replica=0\n"
    )
    assert result.exit_code == 0


@pytest.fixture
def cluster_has_replica_ok_lag(
    patroni_api: PatroniAPI, datadir: Path, tmp_path: Path, old_replica_state: bool
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_has_replica_ok_lag.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_has_replica_ok_lag")
def test_cluster_has_replica_ok_with_count_thresholds_lag(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_has_replica",
            "--warning",
            "@1",
            "--critical",
            "@0",
            "--max-lag",
            "1MB",
        ],
    )
    assert (
        result.stdout
        == "CLUSTERHASREPLICA OK - healthy_replica is 2 | healthy_replica=2;@1;@0 srv2_lag=1024 srv2_sync=0 srv2_timeline=51 srv3_lag=0 srv3_sync=0 srv3_timeline=51 sync_replica=0 unhealthy_replica=0\n"
    )
    assert result.exit_code == 0


@pytest.fixture
def cluster_has_replica_ko(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_has_replica_ko.json"
    patroni_path: Union[str, Path] = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_has_replica_ko")
def test_cluster_has_replica_ko_with_count_thresholds(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_has_replica",
            "--warning",
            "@1",
            "--critical",
            "@0",
        ],
    )
    assert (
        result.stdout
        == "CLUSTERHASREPLICA WARNING - healthy_replica is 1 (outside range @0:1) | healthy_replica=1;@1;@0 srv3_lag=0 srv3_sync=0 srv3_timeline=51 sync_replica=0 unhealthy_replica=1\n"
    )
    assert result.exit_code == 1


@pytest.mark.usefixtures("cluster_has_replica_ko")
def test_cluster_has_replica_ko_with_sync_count_thresholds(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_has_replica",
            "--sync-warning",
            "2:",
            "--sync-critical",
            "1:",
        ],
    )
    # The lag on srv2 is "unknown". We don't handle string in perfstats so we have to scratch all the second node stats
    assert (
        result.stdout
        == "CLUSTERHASREPLICA CRITICAL - sync_replica is 0 (outside range 1:) | healthy_replica=1 srv3_lag=0 srv3_sync=0 srv3_timeline=51 sync_replica=0;2:;1: unhealthy_replica=1\n"
    )
    assert result.exit_code == 2


@pytest.fixture
def cluster_has_replica_ko_lag(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_has_replica_ko_lag.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_has_replica_ko_lag")
def test_cluster_has_replica_ko_with_count_thresholds_and_lag(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_has_replica",
            "--warning",
            "@1",
            "--critical",
            "@0",
            "--max-lag",
            "1MB",
        ],
    )
    assert (
        result.stdout
        == "CLUSTERHASREPLICA CRITICAL - healthy_replica is 0 (outside range @0:0) | healthy_replica=0;@1;@0 srv2_lag=10241024 srv2_sync=0 srv2_timeline=51 srv3_lag=20000000 srv3_sync=0 srv3_timeline=51 sync_replica=0 unhealthy_replica=2\n"
    )
    assert result.exit_code == 2


@pytest.fixture
def cluster_has_replica_ko_wrong_tl(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_has_replica_ko_wrong_tl.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_has_replica_ko_wrong_tl")
def test_cluster_has_replica_ko_wrong_tl(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_has_replica",
            "--warning",
            "@1",
            "--critical",
            "@0",
            "--max-lag",
            "1MB",
        ],
    )
    assert (
        result.stdout
        == "CLUSTERHASREPLICA WARNING - healthy_replica is 1 (outside range @0:1) | healthy_replica=1;@1;@0 srv2_lag=1000000 srv2_sync=0 srv2_timeline=50 srv3_lag=0 srv3_sync=0 srv3_timeline=51 sync_replica=0 unhealthy_replica=1\n"
    )
    assert result.exit_code == 1


@pytest.fixture
def cluster_has_replica_ko_all_replica(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_has_replica_ko_all_replica.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_has_replica_ko_all_replica")
def test_cluster_has_replica_ko_all_replica(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_has_replica",
            "--warning",
            "@1",
            "--critical",
            "@0",
            "--max-lag",
            "1MB",
        ],
    )
    assert (
        result.stdout
        == "CLUSTERHASREPLICA CRITICAL - healthy_replica is 0 (outside range @0:0) | healthy_replica=0;@1;@0 srv1_lag=0 srv1_sync=0 srv1_timeline=51 srv2_lag=0 srv2_sync=0 srv2_timeline=51 srv3_lag=0 srv3_sync=0 srv3_timeline=51 sync_replica=0 unhealthy_replica=3\n"
    )
    assert result.exit_code == 2
