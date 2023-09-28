from click.testing import CliRunner

from check_patroni.cli import main


def test_cluster_has_scheduled_action_ok(fake_restapi) -> None:
    runner = CliRunner()

    fake_restapi("cluster_has_scheduled_action_ok")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_scheduled_action"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERHASSCHEDULEDACTION OK - has_scheduled_actions is 0 | has_scheduled_actions=0;;0 scheduled_restart=0 scheduled_switchover=0\n"
    )


def test_cluster_has_scheduled_action_ko_switchover(fake_restapi) -> None:
    runner = CliRunner()

    fake_restapi("cluster_has_scheduled_action_ko_switchover")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_scheduled_action"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "CLUSTERHASSCHEDULEDACTION CRITICAL - has_scheduled_actions is 1 (outside range 0:0) | has_scheduled_actions=1;;0 scheduled_restart=0 scheduled_switchover=1\n"
    )


def test_cluster_has_scheduled_action_ko_restart(fake_restapi) -> None:
    runner = CliRunner()

    fake_restapi("cluster_has_scheduled_action_ko_restart")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_scheduled_action"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "CLUSTERHASSCHEDULEDACTION CRITICAL - has_scheduled_actions is 1 (outside range 0:0) | has_scheduled_actions=1;;0 scheduled_restart=1 scheduled_switchover=0\n"
    )
