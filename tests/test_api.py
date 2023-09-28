from click.testing import CliRunner

from check_patroni.cli import main


def test_api_status_code_200(runner: CliRunner, fake_restapi) -> None:
    fake_restapi("node_is_pending_restart_ok")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_pending_restart"]
    )
    assert result.exit_code == 0


def test_api_status_code_404(runner: CliRunner, fake_restapi) -> None:
    fake_restapi("Fake test", status=404)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_pending_restart"]
    )
    assert result.exit_code == 3
