from click.testing import CliRunner

from check_patroni.cli import main


def test_node_is_primary_ok(runner: CliRunner, fake_restapi) -> None:
    fake_restapi("node_is_primary_ok")
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_primary"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISPRIMARY OK - This node is the primary with the leader lock. | is_primary=1;;@0\n"
    )


def test_node_is_primary_ko(runner: CliRunner, fake_restapi) -> None:
    fake_restapi("node_is_primary_ko", status=503)
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_primary"])
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISPRIMARY CRITICAL - This node is not the primary with the leader lock. | is_primary=0;;@0\n"
    )
