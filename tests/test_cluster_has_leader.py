from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI


def test_cluster_has_leader_ok(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    with patroni_api.routes({"cluster": "cluster_has_leader_ok.json"}):
        result = runner.invoke(main, ["-e", patroni_api.endpoint, "cluster_has_leader"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERHASLEADER OK - The cluster has a running leader. | has_leader=1;;@0\n"
    )


def test_cluster_has_leader_ok_standby_leader(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    with patroni_api.routes({"cluster": "cluster_has_leader_ok_standby_leader.json"}):
        result = runner.invoke(main, ["-e", patroni_api.endpoint, "cluster_has_leader"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERHASLEADER OK - The cluster has a running leader. | has_leader=1;;@0\n"
    )


def test_cluster_has_leader_ko(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    with patroni_api.routes({"cluster": "cluster_has_leader_ko.json"}):
        result = runner.invoke(main, ["-e", patroni_api.endpoint, "cluster_has_leader"])
    assert result.exit_code == 2
    assert (
        result.stdout
        == "CLUSTERHASLEADER CRITICAL - The cluster has no running leader. | has_leader=0;;@0\n"
    )
