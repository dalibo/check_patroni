from pathlib import Path
from typing import Iterator

import nagiosplugin
import pytest
from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI


@pytest.fixture
def node_tl_has_changed(patroni_api: PatroniAPI) -> Iterator[None]:
    with patroni_api.routes({"patroni": "node_tl_has_changed.json"}):
        yield None


@pytest.mark.usefixtures("node_tl_has_changed")
def test_node_tl_has_changed_ok_with_timeline(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
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


@pytest.mark.usefixtures("node_tl_has_changed")
def test_node_tl_has_changed_ok_with_state_file(
    runner: CliRunner, patroni_api: PatroniAPI, tmp_path: Path
) -> None:
    state_file = tmp_path / "node_tl_has_changed.state_file"
    with state_file.open("w") as f:
        f.write('{"timeline": 58}')

    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "node_tl_has_changed",
            "--state-file",
            str(state_file),
        ],
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODETLHASCHANGED OK - The timeline is still 58. | is_timeline_changed=0;;@1:1 timeline=58\n"
    )


@pytest.mark.usefixtures("node_tl_has_changed")
def test_node_tl_has_changed_ko_with_timeline(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
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


@pytest.mark.usefixtures("node_tl_has_changed")
def test_node_tl_has_changed_ko_with_state_file_and_save(
    runner: CliRunner, patroni_api: PatroniAPI, tmp_path: Path
) -> None:
    state_file = tmp_path / "node_tl_has_changed.state_file"
    with state_file.open("w") as f:
        f.write('{"timeline": 700}')

    # test without saving the new tl
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "node_tl_has_changed",
            "--state-file",
            str(state_file),
        ],
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODETLHASCHANGED CRITICAL - The expected timeline was 700 got 58. | is_timeline_changed=1;;@1:1 timeline=58\n"
    )

    cookie = nagiosplugin.Cookie(state_file)
    cookie.open()
    new_tl = cookie.get("timeline")
    cookie.close()

    assert new_tl == 700

    # test when we save the hash
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "node_tl_has_changed",
            "--state-file",
            str(state_file),
            "--save",
        ],
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODETLHASCHANGED CRITICAL - The expected timeline was 700 got 58. | is_timeline_changed=1;;@1:1 timeline=58\n"
    )

    cookie = nagiosplugin.Cookie(state_file)
    cookie.open()
    new_tl = cookie.get("timeline")
    cookie.close()

    assert new_tl == 58


@pytest.mark.usefixtures("node_tl_has_changed")
def test_node_tl_has_changed_params(
    runner: CliRunner, patroni_api: PatroniAPI, tmp_path: Path
) -> None:
    # This one is placed last because it seems like the exceptions are not flushed from stderr for the next tests.
    fake_state_file = tmp_path / "fake_file_name.state_file"
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "node_tl_has_changed",
            "--timeline",
            "58",
            "--state-file",
            str(fake_state_file),
        ],
    )
    assert result.exit_code == 3
    assert (
        result.stdout
        == "NODETLHASCHANGED UNKNOWN: click.exceptions.UsageError: Either --timeline or --state-file should be provided for this service\n"
    )

    result = runner.invoke(main, ["-e", patroni_api.endpoint, "node_tl_has_changed"])
    assert result.exit_code == 3
    assert (
        result.stdout
        == "NODETLHASCHANGED UNKNOWN: click.exceptions.UsageError: Either --timeline or --state-file should be provided for this service\n"
    )
