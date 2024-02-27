from pathlib import Path
from typing import Iterator, Union

import pytest
from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI, cluster_api_set_replica_running


@pytest.fixture
def cluster_has_leader_ok(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_has_leader_ok.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_has_leader_ok")
def test_cluster_has_leader_ok(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    result = runner.invoke(main, ["-e", patroni_api.endpoint, "cluster_has_leader"])
    assert (
        result.stdout
        == "CLUSTERHASLEADER OK - The cluster has a running leader. | has_leader=1;;@0 is_leader=1 is_standby_leader=0 is_standby_leader_in_arc_rec=0;@1:1\n"
    )
    assert result.exit_code == 0


@pytest.fixture
def cluster_has_leader_ok_standby_leader(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_has_leader_ok_standby_leader.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_has_leader_ok_standby_leader")
def test_cluster_has_leader_ok_standby_leader(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(main, ["-e", patroni_api.endpoint, "cluster_has_leader"])
    assert (
        result.stdout
        == "CLUSTERHASLEADER OK - The cluster has a running leader. | has_leader=1;;@0 is_leader=0 is_standby_leader=1 is_standby_leader_in_arc_rec=0;@1:1\n"
    )
    assert result.exit_code == 0


@pytest.fixture
def cluster_has_leader_ko(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_has_leader_ko.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_has_leader_ko")
def test_cluster_has_leader_ko(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    result = runner.invoke(main, ["-e", patroni_api.endpoint, "cluster_has_leader"])
    assert (
        result.stdout
        == "CLUSTERHASLEADER CRITICAL - The cluster has no running leader or the standby leader is in archive recovery. | has_leader=0;;@0 is_leader=0 is_standby_leader=0 is_standby_leader_in_arc_rec=0;@1:1\n"
    )
    assert result.exit_code == 2


@pytest.fixture
def cluster_has_leader_ko_standby_leader(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_has_leader_ko_standby_leader.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_has_leader_ko_standby_leader")
def test_cluster_has_leader_ko_standby_leader(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(main, ["-e", patroni_api.endpoint, "cluster_has_leader"])
    assert (
        result.stdout
        == "CLUSTERHASLEADER CRITICAL - The cluster has no running leader or the standby leader is in archive recovery. | has_leader=0;;@0 is_leader=0 is_standby_leader=0 is_standby_leader_in_arc_rec=0;@1:1\n"
    )
    assert result.exit_code == 2


@pytest.fixture
def cluster_has_leader_ko_standby_leader_archiving(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = (
        "cluster_has_leader_ko_standby_leader_archiving.json"
    )
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_has_leader_ko_standby_leader_archiving")
def test_cluster_has_leader_ko_standby_leader_archiving(
    runner: CliRunner, patroni_api: PatroniAPI, old_replica_state: bool
) -> None:
    result = runner.invoke(main, ["-e", patroni_api.endpoint, "cluster_has_leader"])
    if old_replica_state:
        assert (
            result.stdout
            == "CLUSTERHASLEADER OK - The cluster has a running leader. | has_leader=1;;@0 is_leader=0 is_standby_leader=1 is_standby_leader_in_arc_rec=0;@1:1\n"
        )
        assert result.exit_code == 0
    else:
        assert (
            result.stdout
            == "CLUSTERHASLEADER WARNING - The cluster has no running leader or the standby leader is in archive recovery. | has_leader=1;;@0 is_leader=0 is_standby_leader=1 is_standby_leader_in_arc_rec=1;@1:1\n"
        )
        assert result.exit_code == 1
