from click.testing import CliRunner

from check_patroni.cli import main


def test_node_is_leader_ok(fake_restapi) -> None:
    runner = CliRunner()

    fake_restapi("node_is_leader_ok")
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_leader"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISLEADER OK - This node is a leader node. | is_leader=1;;@0\n"
    )

    fake_restapi("node_is_leader_ok_standby_leader")
    result = runner.invoke(
        main,
        ["-e", "https://10.20.199.3:8008", "node_is_leader", "--is-standby-leader"],
    )
    print(result.stdout)
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISLEADER OK - This node is a standby leader node. | is_leader=1;;@0\n"
    )


def test_node_is_leader_ko(fake_restapi) -> None:
    runner = CliRunner()

    fake_restapi("node_is_leader_ko", status=503)
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_leader"])
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISLEADER CRITICAL - This node is not a leader node. | is_leader=0;;@0\n"
    )

    fake_restapi("node_is_leader_ko_standby_leader", status=503)
    result = runner.invoke(
        main,
        ["-e", "https://10.20.199.3:8008", "node_is_leader", "--is-standby-leader"],
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISLEADER CRITICAL - This node is not a standby leader node. | is_leader=0;;@0\n"
    )
