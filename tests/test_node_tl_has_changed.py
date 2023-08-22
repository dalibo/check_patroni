import nagiosplugin
from click.testing import CliRunner
from pytest_mock import MockerFixture

from check_patroni.cli import main

from .tools import here, my_mock


def test_node_tl_has_changed_ok_with_timeline(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
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
    assert (
        result.stdout
        == "NODETLHASCHANGED OK - The timeline is still 58. | is_timeline_changed=0;;@1:1 timeline=58\n"
    )


def test_node_tl_has_changed_ok_with_state_file(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
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
    assert (
        result.stdout
        == "NODETLHASCHANGED OK - The timeline is still 58. | is_timeline_changed=0;;@1:1 timeline=58\n"
    )


def test_node_tl_has_changed_ko_with_timeline(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
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
    assert (
        result.stdout
        == "NODETLHASCHANGED CRITICAL - The expected timeline was 700 got 58. | is_timeline_changed=1;;@1:1 timeline=58\n"
    )


def test_node_tl_has_changed_ko_with_state_file_and_save(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    with open(here / "node_tl_has_changed.state_file", "w") as f:
        f.write('{"timeline": 700}')

    my_mock(mocker, "node_tl_has_changed", 200)
    # test without saving the new tl
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
    assert (
        result.stdout
        == "NODETLHASCHANGED CRITICAL - The expected timeline was 700 got 58. | is_timeline_changed=1;;@1:1 timeline=58\n"
    )

    cookie = nagiosplugin.Cookie(here / "node_tl_has_changed.state_file")
    cookie.open()
    new_tl = cookie.get("timeline")
    cookie.close()

    assert new_tl == 700

    # test when we save the hash
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "node_tl_has_changed",
            "--state-file",
            str(here / "node_tl_has_changed.state_file"),
            "--save",
        ],
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODETLHASCHANGED CRITICAL - The expected timeline was 700 got 58. | is_timeline_changed=1;;@1:1 timeline=58\n"
    )

    cookie = nagiosplugin.Cookie(here / "node_tl_has_changed.state_file")
    cookie.open()
    new_tl = cookie.get("timeline")
    cookie.close()

    assert new_tl == 58


def test_node_tl_has_changed_params(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    # This one is placed last because it seems like the exceptions are not flushed from stderr for the next tests.
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
    assert (
        result.stdout
        == "NODETLHASCHANGED UNKNOWN: click.exceptions.UsageError: Either --timeline or --state-file should be provided for this service\n"
    )

    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_tl_has_changed"]
    )
    assert result.exit_code == 3
    assert (
        result.stdout
        == "NODETLHASCHANGED UNKNOWN: click.exceptions.UsageError: Either --timeline or --state-file should be provided for this service\n"
    )
