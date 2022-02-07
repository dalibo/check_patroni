from pytest_mock import MockerFixture

from click.testing import CliRunner

from check_patroni.cli import main
from tools import my_mock


def test_cluster_node_count_ok(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_node_count_ok", 200)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_node_count"]
    )
    assert result.exit_code == 0


def test_cluster_node_count_ok_with_thresholds(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_node_count_ok", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_node_count",
            "--warning",
            "@0:1",
            "--critical",
            "@2",
            "--running-warning",
            "@2",
            "--running-critical",
            "@0:1",
        ],
    )
    assert result.exit_code == 0


def test_cluster_node_count_running_warning(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_node_count_running_warning", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_node_count",
            "--running-warning",
            "@2",
            "--running-critical",
            "@0:1",
        ],
    )
    assert result.exit_code == 1


def test_cluster_node_count_running_critical(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_node_count_running_critical", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_node_count",
            "--running-warning",
            "@2",
            "--running-critical",
            "@0:1",
        ],
    )
    assert result.exit_code == 2


def test_cluster_node_count_warning(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_node_count_warning", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_node_count",
            "--warning",
            "@2",
            "--critical",
            "@0:1",
        ],
    )
    assert result.exit_code == 1


def test_cluster_node_count_critical(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_node_count_critical", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_node_count",
            "--warning",
            "@2",
            "--critical",
            "@0:1",
        ],
    )
    assert result.exit_code == 2
