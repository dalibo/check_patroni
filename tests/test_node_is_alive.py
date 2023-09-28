from click.testing import CliRunner

from check_patroni.cli import main


def test_node_is_alive_ok(runner: CliRunner, fake_restapi) -> None:
    fake_restapi(None)
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_alive"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISALIVE OK - This node is alive (patroni is running). | is_alive=1;;@0\n"
    )


def test_node_is_alive_ko(runner: CliRunner, fake_restapi) -> None:
    fake_restapi(None, status=404)
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_alive"])
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISALIVE CRITICAL - This node is not alive (patroni is not running). | is_alive=0;;@0\n"
    )
