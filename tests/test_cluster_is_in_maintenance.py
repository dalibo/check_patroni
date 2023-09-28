from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI


def test_cluster_is_in_maintenance_ok(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    with patroni_api.routes({"cluster": "cluster_is_in_maintenance_ok.json"}):
        result = runner.invoke(
            main, ["-e", patroni_api.endpoint, "cluster_is_in_maintenance"]
        )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERISINMAINTENANCE OK - is_in_maintenance is 0 | is_in_maintenance=0;;0\n"
    )


def test_cluster_is_in_maintenance_ko(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    with patroni_api.routes({"cluster": "cluster_is_in_maintenance_ko.json"}):
        result = runner.invoke(
            main, ["-e", patroni_api.endpoint, "cluster_is_in_maintenance"]
        )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "CLUSTERISINMAINTENANCE CRITICAL - is_in_maintenance is 1 (outside range 0:0) | is_in_maintenance=1;;0\n"
    )


def test_cluster_is_in_maintenance_ok_pause_false(
    runner: CliRunner, patroni_api: PatroniAPI
) -> None:
    with patroni_api.routes(
        {"cluster": "cluster_is_in_maintenance_ok_pause_false.json"}
    ):
        result = runner.invoke(
            main, ["-e", patroni_api.endpoint, "cluster_is_in_maintenance"]
        )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERISINMAINTENANCE OK - is_in_maintenance is 0 | is_in_maintenance=0;;0\n"
    )
