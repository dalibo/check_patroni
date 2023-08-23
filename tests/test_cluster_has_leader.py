from click.testing import CliRunner
from pytest_mock import MockerFixture

from check_patroni.cli import main

from .tools import my_mock


def test_cluster_has_leader_ok(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_leader_ok", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_leader"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERHASLEADER OK - The cluster has a running leader. | has_leader=1;;@0\n"
    )


def test_cluster_has_leader_ok_standby_leader(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_leader_ok_standby_leader", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_leader"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERHASLEADER OK - The cluster has a running leader. | has_leader=1;;@0\n"
    )


def test_cluster_has_leader_ko(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_leader_ko", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_leader"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "CLUSTERHASLEADER CRITICAL - The cluster has no running leader. | has_leader=0;;@0\n"
    )
