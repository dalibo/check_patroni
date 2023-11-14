from pathlib import Path
from typing import Iterator, Union

import pytest
from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI, cluster_api_set_replica_running


@pytest.fixture
def cluster_node_count_ok(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_node_count_ok.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_node_count_ok")
def test_cluster_node_count_ok(
    runner: CliRunner, patroni_api: PatroniAPI, old_replica_state: bool
) -> None:
    result = runner.invoke(main, ["-e", patroni_api.endpoint, "cluster_node_count"])
    if old_replica_state:
        assert (
            result.output
            == "CLUSTERNODECOUNT OK - members is 3 | healthy_members=3 members=3 role_leader=1 role_replica=2 state_running=3\n"
        )
    else:
        assert (
            result.output
            == "CLUSTERNODECOUNT OK - members is 3 | healthy_members=3 members=3 role_leader=1 role_replica=2 state_running=1 state_streaming=2\n"
        )
    assert result.exit_code == 0


@pytest.mark.usefixtures("cluster_node_count_ok")
def test_cluster_node_count_ok_with_thresholds(
    runner: CliRunner, patroni_api: PatroniAPI, old_replica_state: bool
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_node_count",
            "--warning",
            "@0:1",
            "--critical",
            "@2",
            "--healthy-warning",
            "@2",
            "--healthy-critical",
            "@0:1",
        ],
    )
    if old_replica_state:
        assert (
            result.output
            == "CLUSTERNODECOUNT OK - members is 3 | healthy_members=3;@2;@1 members=3;@1;@2 role_leader=1 role_replica=2 state_running=3\n"
        )
    else:
        assert (
            result.output
            == "CLUSTERNODECOUNT OK - members is 3 | healthy_members=3;@2;@1 members=3;@1;@2 role_leader=1 role_replica=2 state_running=1 state_streaming=2\n"
        )
    assert result.exit_code == 0


@pytest.fixture
def cluster_node_count_healthy_warning(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_node_count_healthy_warning.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_node_count_healthy_warning")
def test_cluster_node_count_healthy_warning(
    runner: CliRunner, patroni_api: PatroniAPI, old_replica_state: bool
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_node_count",
            "--healthy-warning",
            "@2",
            "--healthy-critical",
            "@0:1",
        ],
    )
    if old_replica_state:
        assert (
            result.output
            == "CLUSTERNODECOUNT WARNING - healthy_members is 2 (outside range @0:2) | healthy_members=2;@2;@1 members=2 role_leader=1 role_replica=1 state_running=2\n"
        )
    else:
        assert (
            result.output
            == "CLUSTERNODECOUNT WARNING - healthy_members is 2 (outside range @0:2) | healthy_members=2;@2;@1 members=2 role_leader=1 role_replica=1 state_running=1 state_streaming=1\n"
        )
    assert result.exit_code == 1


@pytest.fixture
def cluster_node_count_healthy_critical(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_node_count_healthy_critical.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_node_count_healthy_critical")
def test_cluster_node_count_healthy_critical(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_node_count",
            "--healthy-warning",
            "@2",
            "--healthy-critical",
            "@0:1",
        ],
    )
    assert (
        result.output
        == "CLUSTERNODECOUNT CRITICAL - healthy_members is 1 (outside range @0:1) | healthy_members=1;@2;@1 members=3 role_leader=1 role_replica=2 state_running=1 state_start_failed=2\n"
    )
    assert result.exit_code == 2


@pytest.fixture
def cluster_node_count_warning(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_node_count_warning.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_node_count_warning")
def test_cluster_node_count_warning(
    runner: CliRunner, patroni_api: PatroniAPI, old_replica_state: bool
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_node_count",
            "--warning",
            "@2",
            "--critical",
            "@0:1",
        ],
    )
    if old_replica_state:
        assert (
            result.stdout
            == "CLUSTERNODECOUNT WARNING - members is 2 (outside range @0:2) | healthy_members=2 members=2;@2;@1 role_leader=1 role_replica=1 state_running=2\n"
        )
    else:
        assert (
            result.stdout
            == "CLUSTERNODECOUNT WARNING - members is 2 (outside range @0:2) | healthy_members=2 members=2;@2;@1 role_leader=1 role_replica=1 state_running=1 state_streaming=1\n"
        )
    assert result.exit_code == 1


@pytest.fixture
def cluster_node_count_critical(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_node_count_critical.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_node_count_critical")
def test_cluster_node_count_critical(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_node_count",
            "--warning",
            "@2",
            "--critical",
            "@0:1",
        ],
    )
    assert (
        result.stdout
        == "CLUSTERNODECOUNT CRITICAL - members is 1 (outside range @0:1) | healthy_members=1 members=1;@2;@1 role_leader=1 state_running=1\n"
    )
    assert result.exit_code == 2


@pytest.fixture
def cluster_node_count_ko_in_archive_recovery(
    patroni_api: PatroniAPI, old_replica_state: bool, datadir: Path, tmp_path: Path
) -> Iterator[None]:
    cluster_path: Union[str, Path] = "cluster_node_count_ko_in_archive_recovery.json"
    patroni_path = "cluster_has_replica_patroni_verion_3.1.0.json"
    if old_replica_state:
        cluster_path = cluster_api_set_replica_running(datadir / cluster_path, tmp_path)
        patroni_path = "cluster_has_replica_patroni_verion_3.0.0.json"
    with patroni_api.routes({"cluster": cluster_path, "patroni": patroni_path}):
        yield None


@pytest.mark.usefixtures("cluster_node_count_ko_in_archive_recovery")
def test_cluster_node_count_ko_in_archive_recovery(
    runner: CliRunner, patroni_api: PatroniAPI, old_replica_state: bool
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_node_count",
            "--healthy-warning",
            "@2",
            "--healthy-critical",
            "@0:1",
        ],
    )
    if old_replica_state:
        assert (
            result.stdout
            == "CLUSTERNODECOUNT OK - members is 3 | healthy_members=3;@2;@1 members=3 role_replica=2 role_standby_leader=1 state_running=3\n"
        )
        assert result.exit_code == 0
    else:
        assert (
            result.stdout
            == "CLUSTERNODECOUNT CRITICAL - healthy_members is 1 (outside range @0:1) | healthy_members=1;@2;@1 members=3 role_replica=2 role_standby_leader=1 state_in_archive_recovery=2 state_streaming=1\n"
        )
        assert result.exit_code == 2
