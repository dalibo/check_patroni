from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI


def test_cluster_has_scheduled_action_ok(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    with patroni_api.routes({"cluster": "cluster_has_scheduled_action_ok.json"}):
        result = runner.invoke(
            main, ["-e", patroni_api.endpoint, "cluster_has_scheduled_action"]
        )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERHASSCHEDULEDACTION OK - has_scheduled_actions is 0 | has_scheduled_actions=0;;0 scheduled_restart=0 scheduled_switchover=0\n"
    )


def test_cluster_has_scheduled_action_ko_switchover(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    with patroni_api.routes(
        {"cluster": "cluster_has_scheduled_action_ko_switchover.json"}
    ):
        result = runner.invoke(
            main, ["-e", patroni_api.endpoint, "cluster_has_scheduled_action"]
        )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "CLUSTERHASSCHEDULEDACTION CRITICAL - has_scheduled_actions is 1 (outside range 0:0) | has_scheduled_actions=1;;0 scheduled_restart=0 scheduled_switchover=1\n"
    )


def test_cluster_has_scheduled_action_ko_restart(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    with patroni_api.routes(
        {"cluster": "cluster_has_scheduled_action_ko_restart.json"}
    ):
        result = runner.invoke(
            main, ["-e", patroni_api.endpoint, "cluster_has_scheduled_action"]
        )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "CLUSTERHASSCHEDULEDACTION CRITICAL - has_scheduled_actions is 1 (outside range 0:0) | has_scheduled_actions=1;;0 scheduled_restart=1 scheduled_switchover=0\n"
    )
