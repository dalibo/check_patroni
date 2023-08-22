from click.testing import CliRunner
from pytest_mock import MockerFixture

from check_patroni.cli import main

from .tools import my_mock


def test_api_status_code_200(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_is_pending_restart_ok", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_pending_restart"]
    )
    assert result.exit_code == 0


def test_api_status_code_404(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "Fake test", 404)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_pending_restart"]
    )
    assert result.exit_code == 3
