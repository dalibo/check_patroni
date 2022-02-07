from click.testing import CliRunner
from pytest_mock import MockerFixture

from check_patroni.cli import main

import nagiosplugin

from tools import my_mock, here


def test_node_tl_has_changed_params(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_tl_has_changed", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "node_tl_has_changed",
            "--timeline",
            "58",
            "--state-file",
            str(here / "fake_file_name.state_file"),
        ],
    )
    assert result.exit_code == 3

    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_tl_has_changed"]
    )
    assert result.exit_code == 3


def test_node_tl_has_changed_ok_with_timeline(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_tl_has_changed", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "node_tl_has_changed",
            "--timeline",
            "58",
        ],
    )
    assert result.exit_code == 0


def test_node_tl_has_changed_ok_with_state_file(mocker: MockerFixture) -> None:
    runner = CliRunner()

    with open(here / "node_tl_has_changed.state_file", "w") as f:
        f.write('{"timeline": 58}')

    my_mock(mocker, "node_tl_has_changed", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "node_tl_has_changed",
            "--state-file",
            str(here / "node_tl_has_changed.state_file"),
        ],
    )
    assert result.exit_code == 0


def test_node_tl_has_changed_ko_with_timeline(mocker: MockerFixture) -> None:
    runner = CliRunner()

    my_mock(mocker, "node_tl_has_changed", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "node_tl_has_changed",
            "--timeline",
            "700",
        ],
    )
    assert result.exit_code == 2


def test_node_tl_has_changed_ko_with_state_file(mocker: MockerFixture) -> None:
    runner = CliRunner()

    with open(here / "node_tl_has_changed.state_file", "w") as f:
        f.write('{"timeline": 700}')

    my_mock(mocker, "node_tl_has_changed", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "node_tl_has_changed",
            "--state-file",
            str(here / "node_tl_has_changed.state_file"),
        ],
    )
    assert result.exit_code == 2

    # the new timeline was saved
    cookie = nagiosplugin.Cookie(here / "node_tl_has_changed.state_file")
    cookie.open()
    new_tl = cookie.get("timeline")
    cookie.close()

    assert new_tl == 58
