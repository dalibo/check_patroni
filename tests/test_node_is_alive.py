from pathlib import Path

from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI


def test_node_is_alive_ok(
    runner: CliRunner, patroni_api: PatroniAPI, tmp_path: Path
) -> None:
    liveness = tmp_path / "liveness"
    liveness.touch()
    with patroni_api.routes({"liveness": liveness}):
        result = runner.invoke(main, ["-e", patroni_api.endpoint, "node_is_alive"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISALIVE OK - This node is alive (patroni is running). | is_alive=1;;@0\n"
    )


def test_node_is_alive_ko(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    result = runner.invoke(main, ["-e", patroni_api.endpoint, "node_is_alive"])
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISALIVE CRITICAL - This node is not alive (patroni is not running). | is_alive=0;;@0\n"
    )
