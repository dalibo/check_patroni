from click.testing import CliRunner

from check_patroni.cli import main


def test_node_is_pending_restart_ok(runner: CliRunner, fake_restapi) -> None:
    fake_restapi("node_is_pending_restart_ok")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_pending_restart"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISPENDINGRESTART OK - This node doesn't have the pending restart flag. | is_pending_restart=0;;0\n"
    )


def test_node_is_pending_restart_ko(runner: CliRunner, fake_restapi) -> None:
    fake_restapi("node_is_pending_restart_ko")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_pending_restart"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISPENDINGRESTART CRITICAL - This node has the pending restart flag. | is_pending_restart=1;;0\n"
    )
