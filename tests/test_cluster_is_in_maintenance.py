from click.testing import CliRunner

from check_patroni.cli import main


def test_cluster_is_in_maintenance_ok(fake_restapi) -> None:
    runner = CliRunner()

    fake_restapi("cluster_is_in_maintenance_ok")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_is_in_maintenance"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERISINMAINTENANCE OK - is_in_maintenance is 0 | is_in_maintenance=0;;0\n"
    )


def test_cluster_is_in_maintenance_ko(fake_restapi) -> None:
    runner = CliRunner()

    fake_restapi("cluster_is_in_maintenance_ko")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_is_in_maintenance"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "CLUSTERISINMAINTENANCE CRITICAL - is_in_maintenance is 1 (outside range 0:0) | is_in_maintenance=1;;0\n"
    )


def test_cluster_is_in_maintenance_ok_pause_false(fake_restapi) -> None:
    runner = CliRunner()

    fake_restapi("cluster_is_in_maintenance_ok_pause_false")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "cluster_is_in_maintenance"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "CLUSTERISINMAINTENANCE OK - is_in_maintenance is 0 | is_in_maintenance=0;;0\n"
    )
