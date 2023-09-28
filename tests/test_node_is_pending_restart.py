from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI


def test_node_is_pending_restart_ok(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    with patroni_api.routes({"patroni": "node_is_pending_restart_ok.json"}):
        result = runner.invoke(
            main, ["-e", patroni_api.endpoint, "node_is_pending_restart"]
        )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISPENDINGRESTART OK - This node doesn't have the pending restart flag. | is_pending_restart=0;;0\n"
    )


def test_node_is_pending_restart_ko(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    with patroni_api.routes({"patroni": "node_is_pending_restart_ko.json"}):
        result = runner.invoke(
            main, ["-e", patroni_api.endpoint, "node_is_pending_restart"]
        )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISPENDINGRESTART CRITICAL - This node has the pending restart flag. | is_pending_restart=1;;0\n"
    )
