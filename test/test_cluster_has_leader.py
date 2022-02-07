from pytest_mock import MockerFixture

from click.testing import CliRunner

from check_patroni.cli import main
from tools import my_mock


def test_cluster_has_leader_ok(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_leader_ok", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_leader"]
    )
    assert result.exit_code == 0
    # FIXME the data seems to not be written to stdout yet ...
    # assert "CLUSTERHASLEADER OK - has_leader is 1 | has_leader=1;;@0" in result.output


def test_cluster_has_leader_ko(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_leader_ko", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_leader"]
    )
    assert result.exit_code == 2
    # assert "CLUSTERHASLEADER CRITICAL - has_leader is 0 (outside range @0:0) | has_leader=0;;@0" in result.output
