from pathlib import Path
from typing import Iterator

import nagiosplugin
import pytest
from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI


@pytest.fixture(scope="module", autouse=True)
def cluster_config_has_changed(patroni_api: PatroniAPI) -> Iterator[None]:
    with patroni_api.routes({"config": "cluster_config_has_changed.json"}):
        yield None


def test_cluster_config_has_changed_ok_with_hash(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_config_has_changed",
            "--hash",
            "30022c301991e7395182b1134683e518",
        ],
    )
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED OK - The hash of patroni's dynamic configuration has not changed (30022c301991e7395182b1134683e518). | is_configuration_changed=0;;@1:1\n"
    )
    assert result.exit_code == 0


def test_cluster_config_has_changed_ok_with_state_file(
    runner: CliRunner, patroni_api: PatroniAPI, tmp_path: Path
) -> None:
    state_file = tmp_path / "cluster_config_has_changed.state_file"
    with state_file.open("w") as f:
        f.write('{"hash": "30022c301991e7395182b1134683e518"}')

    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_config_has_changed",
            "--state-file",
            str(state_file),
        ],
    )
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED OK - The hash of patroni's dynamic configuration has not changed (30022c301991e7395182b1134683e518). | is_configuration_changed=0;;@1:1\n"
    )
    assert result.exit_code == 0


def test_cluster_config_has_changed_ko_with_hash(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_config_has_changed",
            "--hash",
            "96b12d82571473d13e890b8937ffffff",
        ],
    )
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED CRITICAL - The hash of patroni's dynamic configuration has changed. The old hash was 96b12d82571473d13e890b8937ffffff. | is_configuration_changed=1;;@1:1\n"
    )
    assert result.exit_code == 2


def test_cluster_config_has_changed_ko_with_state_file_and_save(
    runner: CliRunner, patroni_api: PatroniAPI, tmp_path: Path
) -> None:
    state_file = tmp_path / "cluster_config_has_changed.state_file"
    with state_file.open("w") as f:
        f.write('{"hash": "96b12d82571473d13e890b8937ffffff"}')

    # test without saving the new hash
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_config_has_changed",
            "--state-file",
            str(state_file),
        ],
    )
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED CRITICAL - The hash of patroni's dynamic configuration has changed. The old hash was 96b12d82571473d13e890b8937ffffff. | is_configuration_changed=1;;@1:1\n"
    )
    assert result.exit_code == 2

    state_file = tmp_path / "cluster_config_has_changed.state_file"
    cookie = nagiosplugin.Cookie(state_file)
    cookie.open()
    new_config_hash = cookie.get("hash")
    cookie.close()

    assert new_config_hash == "96b12d82571473d13e890b8937ffffff"

    # test when we save the hash
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_config_has_changed",
            "--state-file",
            str(state_file),
            "--save",
        ],
    )
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED CRITICAL - The hash of patroni's dynamic configuration has changed. The old hash was 96b12d82571473d13e890b8937ffffff. | is_configuration_changed=1;;@1:1\n"
    )
    assert result.exit_code == 2

    cookie = nagiosplugin.Cookie(state_file)
    cookie.open()
    new_config_hash = cookie.get("hash")
    cookie.close()

    assert new_config_hash == "30022c301991e7395182b1134683e518"


def test_cluster_config_has_changed_params(
    runner: CliRunner, patroni_api: PatroniAPI, tmp_path: Path
) -> None:
    # This one is placed last because it seems like the exceptions are not flushed from stderr for the next tests.
    fake_state_file = tmp_path / "fake_file_name.state_file"
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
            "cluster_config_has_changed",
            "--hash",
            "640df9f0211c791723f18fc3ed9dbb95",
            "--state-file",
            str(fake_state_file),
        ],
    )
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED UNKNOWN: click.exceptions.UsageError: Either --hash or --state-file should be provided for this service\n"
    )
    assert result.exit_code == 3

    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_config_has_changed"]
    )
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED UNKNOWN: click.exceptions.UsageError: Either --hash or --state-file should be provided for this service\n"
    )
