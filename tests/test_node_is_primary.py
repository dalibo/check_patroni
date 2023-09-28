from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI


def test_node_is_primary_ok(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    with patroni_api.routes({"primary": "node_is_primary_ok.json"}):
        result = runner.invoke(main, ["-e", patroni_api.endpoint, "node_is_primary"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISPRIMARY OK - This node is the primary with the leader lock. | is_primary=1;;@0\n"
    )


def test_node_is_primary_ko(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    result = runner.invoke(main, ["-e", patroni_api.endpoint, "node_is_primary"])
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISPRIMARY CRITICAL - This node is not the primary with the leader lock. | is_primary=0;;@0\n"
    )
