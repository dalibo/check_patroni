from click.testing import CliRunner
from pytest_mock import MockerFixture

from check_patroni.cli import main

from tools import my_mock


# TODO Lag threshold tests
def test_cluster_has_relica_ok(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ok", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_has_replica"]
    )
    assert result.exit_code == 0


def test_cluster_has_replica_ok_with_count_thresholds(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_has_replica_ko", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_has_replica",
            "--warninng",
            "@2",
            "--critical",
            "@0:1",
        ],
    )
    assert result.exit_code == 2
