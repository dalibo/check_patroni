from click.testing import CliRunner

from check_patroni.cli import main


def test_node_is_replica_ok(fake_restapi) -> None:
    runner = CliRunner()

    fake_restapi("node_is_replica_ok")
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_replica"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISREPLICA OK - This node is a running replica with no noloadbalance tag. | is_replica=1;;@0\n"
    )


def test_node_is_replica_ko(fake_restapi) -> None:
    runner = CliRunner()

    fake_restapi("node_is_replica_ko", status=503)
    result = runner.invoke(main, ["-e", "https://10.20.199.3:8008", "node_is_replica"])
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISREPLICA CRITICAL - This node is not a running replica with no noloadbalance tag. | is_replica=0;;@0\n"
    )


def test_node_is_replica_ko_lag(fake_restapi) -> None:
    runner = CliRunner()

    # We don't do the check ourselves, patroni does it and changes the return code
    fake_restapi("node_is_replica_ok", status=503)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_replica", "--max-lag", "100"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISREPLICA CRITICAL - This node is not a running replica with no noloadbalance tag and a lag under 100. | is_replica=0;;@0\n"
    )

    fake_restapi("node_is_replica_ok", status=503)
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "node_is_replica",
            "--is-async",
            "--max-lag",
            "100",
        ],
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISREPLICA CRITICAL - This node is not a running asynchronous replica with no noloadbalance tag and a lag under 100. | is_replica=0;;@0\n"
    )


def test_node_is_replica_sync_ok(fake_restapi) -> None:
    runner = CliRunner()

    # We don't do the check ourselves, patroni does it and changes the return code
    fake_restapi("node_is_replica_ok")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_replica", "--is-sync"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISREPLICA OK - This node is a running synchronous replica with no noloadbalance tag. | is_replica=1;;@0\n"
    )


def test_node_is_replica_sync_ko(fake_restapi) -> None:
    runner = CliRunner()

    # We don't do the check ourselves, patroni does it and changes the return code
    fake_restapi("node_is_replica_ok", status=503)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_replica", "--is-sync"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISREPLICA CRITICAL - This node is not a running synchronous replica with no noloadbalance tag. | is_replica=0;;@0\n"
    )


def test_node_is_replica_async_ok(fake_restapi) -> None:
    runner = CliRunner()

    # We don't do the check ourselves, patroni does it and changes the return code
    fake_restapi("node_is_replica_ok")
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_replica", "--is-async"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISREPLICA OK - This node is a running asynchronous replica with no noloadbalance tag. | is_replica=1;;@0\n"
    )


def test_node_is_replica_async_ko(fake_restapi) -> None:
    runner = CliRunner()

    # We don't do the check ourselves, patroni does it and changes the return code
    fake_restapi("node_is_replica_ok", status=503)
    result = runner.invoke(
        main, ["-e", "https://10.20.199.3:8008", "node_is_replica", "--is-async"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISREPLICA CRITICAL - This node is not a running asynchronous replica with no noloadbalance tag. | is_replica=0;;@0\n"
    )


def test_node_is_replica_params(fake_restapi) -> None:
    runner = CliRunner()

    # We don't do the check ourselves, patroni does it and changes the return code
    fake_restapi("node_is_replica_ok")
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "node_is_replica",
            "--is-async",
            "--is-sync",
        ],
    )
    assert result.exit_code == 3
    assert (
        result.stdout
        == "NODEISREPLICA UNKNOWN: click.exceptions.UsageError: --is-sync and --is-async cannot be provided at the same time for this service\n"
    )

    # We don't do the check ourselves, patroni does it and changes the return code
    fake_restapi("node_is_replica_ok")
    result = runner.invoke(
        main,
        [
            "-e",
            "https://10.20.199.3:8008",
            "node_is_replica",
            "--is-sync",
            "--max-lag",
            "1MB",
        ],
    )
    assert result.exit_code == 3
    assert (
        result.stdout
        == "NODEISREPLICA UNKNOWN: click.exceptions.UsageError: --is-sync and --max-lag cannot be provided at the same time for this service\n"
    )
