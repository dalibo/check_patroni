import nagiosplugin
from click.testing import CliRunner
from pytest_mock import MockerFixture

from check_patroni.cli import main

from .tools import here, my_mock


def test_cluster_config_has_changed_ok_with_hash(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_config_has_changed", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_config_has_changed",
            "--hash",
            "96b12d82571473d13e890b893734e731",
        ],
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED OK - The hash of patroni's dynamic configuration has not changed (96b12d82571473d13e890b893734e731). | is_configuration_changed=0;;@1:1\n"
    )


def test_cluster_config_has_changed_ok_with_state_file(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    with open(here / "cluster_config_has_changed.state_file", "w") as f:
        f.write('{"hash": "96b12d82571473d13e890b893734e731"}')

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
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED OK - The hash of patroni's dynamic configuration has not changed (96b12d82571473d13e890b893734e731). | is_configuration_changed=0;;@1:1\n"
    )


def test_cluster_config_has_changed_ko_with_hash(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    runner = CliRunner()

    my_mock(mocker, "cluster_config_has_changed", 200)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_config_has_changed",
            "--hash",
            "96b12d82571473d13e890b8937ffffff",
        ],
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED CRITICAL - The hash of patroni's dynamic configuration has changed. The old hash was 96b12d82571473d13e890b8937ffffff. | is_configuration_changed=1;;@1:1\n"
    )


def test_cluster_config_has_changed_ko_with_state_file_and_save(
    mocker: MockerFixture,
    use_old_replica_state: bool,
) -> None:
    runner = CliRunner()

    with open(here / "cluster_config_has_changed.state_file", "w") as f:
        f.write('{"hash": "96b12d82571473d13e890b8937ffffff"}')

    my_mock(mocker, "cluster_config_has_changed", 200)
    # test without saving the new hash
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
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED CRITICAL - The hash of patroni's dynamic configuration has changed. The old hash was 96b12d82571473d13e890b8937ffffff. | is_configuration_changed=1;;@1:1\n"
    )

    cookie = nagiosplugin.Cookie(here / "cluster_config_has_changed.state_file")
    cookie.open()
    new_config_hash = cookie.get("hash")
    cookie.close()

    assert new_config_hash == "96b12d82571473d13e890b8937ffffff"

    # test when we save the hash
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "cluster_config_has_changed",
            "--state-file",
            str(here / "cluster_config_has_changed.state_file"),
            "--save",
        ],
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED CRITICAL - The hash of patroni's dynamic configuration has changed. The old hash was 96b12d82571473d13e890b8937ffffff. | is_configuration_changed=1;;@1:1\n"
    )

    cookie = nagiosplugin.Cookie(here / "cluster_config_has_changed.state_file")
    cookie.open()
    new_config_hash = cookie.get("hash")
    cookie.close()

    assert new_config_hash == "96b12d82571473d13e890b893734e731"


def test_cluster_config_has_changed_params(
    mocker: MockerFixture, use_old_replica_state: bool
) -> None:
    # This one is placed last because it seems like the exceptions are not flushed from stderr for the next tests.
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
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED UNKNOWN: click.exceptions.UsageError: Either --hash or --state-file should be provided for this service\n"
    )

    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_config_has_changed"]
    )
    assert result.exit_code == 3
    assert (
        result.stdout
        == "CLUSTERCONFIGHASCHANGED UNKNOWN: click.exceptions.UsageError: Either --hash or --state-file should be provided for this service\n"
    )
