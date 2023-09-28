from click.testing import CliRunner

from check_patroni.cli import main


def test_cluster_has_leader_ok(runner: CliRunner, fake_restapi) -> None:
    fake_restapi("cluster_has_leader_ok")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_leader"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERHASLEADER OK - The cluster has a running leader. | has_leader=1;;@0\n"
    )


def test_cluster_has_leader_ok_standby_leader(runner: CliRunner, fake_restapi) -> None:
    fake_restapi("cluster_has_leader_ok_standby_leader")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_leader"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERHASLEADER OK - The cluster has a running leader. | has_leader=1;;@0\n"
    )


def test_cluster_has_leader_ko(runner: CliRunner, fake_restapi) -> None:
    fake_restapi("cluster_has_leader_ko")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_leader"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "CLUSTERHASLEADER CRITICAL - The cluster has no running leader. | has_leader=0;;@0\n"
    )
