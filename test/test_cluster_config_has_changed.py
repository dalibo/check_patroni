from pytest_mock import MockerFixture

import nagiosplugin
from click.testing import CliRunner

from check_patroni.cli import main
from tools import my_mock, here


def test_cluster_config_has_changed_params(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_config_has_changed", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_config_has_changed",
            "--hash",
            "640df9f0211c791723f18fc3ed9dbb95",
            "--state-file",
            str(here / "fake_file_name.state_file"),
        ],
    )
    assert result.exit_code == 3

    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_config_has_changed"]
    )
    assert result.exit_code == 3


def test_cluster_config_has_changed_ok_with_hash(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_config_has_changed", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_config_has_changed",
            "--hash",
            "640df9f0211c791723f18fc3ed9dbb95",
        ],
    )
    assert result.exit_code == 0


def test_cluster_config_has_changed_ok_with_state_file(mocker: MockerFixture) -> None:
    runner = CliRunner()

    with open(here / "cluster_config_has_changed.state_file", "w") as f:
        f.write('{"hash": "640df9f0211c791723f18fc3ed9dbb95"}')

    my_mock(mocker, "cluster_config_has_changed", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_config_has_changed",
            "--state-file",
            str(here / "cluster_config_has_changed.state_file"),
        ],
    )
    assert result.exit_code == 0


def test_cluster_config_has_changed_ko_with_hash(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_config_has_changed", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_config_has_changed",
            "--hash",
            "640df9f0211c791723f18fc3edffffff",
        ],
    )
    assert result.exit_code == 2


def test_cluster_config_has_changed_ko_with_state_file(mocker: MockerFixture) -> None:
    runner = CliRunner()

    with open(here / "cluster_config_has_changed.state_file", "w") as f:
        f.write('{"hash": "640df9f0211c791723f18fc3edffffff"}')

    my_mock(mocker, "cluster_config_has_changed", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_config_has_changed",
            "--state-file",
            str(here / "cluster_config_has_changed.state_file"),
        ],
    )
    assert result.exit_code == 2

    # the new hash was saved
    cookie = nagiosplugin.Cookie(here / "cluster_config_has_changed.state_file")
    cookie.open()
    new_config_hash = cookie.get("hash")
    cookie.close()

    assert new_config_hash == "640df9f0211c791723f18fc3ed9dbb95"
