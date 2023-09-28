from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI


def test_api_status_code_200(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    with patroni_api.routes({"patroni": "node_is_pending_restart_ok.json"}):
        result = runner.invoke(
            main, ["-e", patroni_api.endpoint, "node_is_pending_restart"]
        )
    assert result.exit_code == 0


def test_api_status_code_404(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    result = runner.invoke(
        main, ["-e", patroni_api.endpoint, "node_is_pending_restart"]
    )
    assert result.exit_code == 3
