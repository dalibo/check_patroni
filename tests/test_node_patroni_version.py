from click.testing import CliRunner

from check_patroni.cli import main


def test_node_patroni_version_ok(fake_restapi) -> None:
    runner = CliRunner()

    fake_restapi("node_patroni_version")
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "node_patroni_version",
            "--patroni-version",
            "2.0.2",
        ],
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEPATRONIVERSION OK - Patroni's version is 2.0.2. | is_version_ok=1;;@0\n"
    )


def test_node_patroni_version_ko(fake_restapi) -> None:
    runner = CliRunner()

    fake_restapi("node_patroni_version")
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "node_patroni_version",
            "--patroni-version",
            "1.0.0",
        ],
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEPATRONIVERSION CRITICAL - Patroni's version is not 1.0.0. | is_version_ok=0;;@0\n"
    )
