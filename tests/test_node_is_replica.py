from typing import Iterator

import pytest
from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI


@pytest.fixture
def node_is_replica_ok(patroni_api: PatroniAPI) -> Iterator[None]:
    with patroni_api.routes(
        {
            k: "node_is_replica_ok.json"
            for k in ("replica", "synchronous", "asynchronous")
        }
    ):
        yield None


@pytest.mark.usefixtures("node_is_replica_ok")
def test_node_is_replica_ok(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    result = runner.invoke(main, ["-e", patroni_api.endpoint, "node_is_replica"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISREPLICA OK - This node is a running replica with no noloadbalance tag. | is_replica=1;;@0\n"
    )


def test_node_is_replica_ko(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    result = runner.invoke(main, ["-e", patroni_api.endpoint, "node_is_replica"])
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISREPLICA CRITICAL - This node is not a running replica with no noloadbalance tag. | is_replica=0;;@0\n"
    )


def test_node_is_replica_ko_lag(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    # We don't do the check ourselves, patroni does it and changes the return code
    result = runner.invoke(
        main, ["-e", patroni_api.endpoint, "node_is_replica", "--max-lag", "100"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISREPLICA CRITICAL - This node is not a running replica with no noloadbalance tag and a lag under 100. | is_replica=0;;@0\n"
    )

    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
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


@pytest.mark.usefixtures("node_is_replica_ok")
def test_node_is_replica_sync_ok(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    # We don't do the check ourselves, patroni does it and changes the return code
    result = runner.invoke(
        main, ["-e", patroni_api.endpoint, "node_is_replica", "--is-sync"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISREPLICA OK - This node is a running synchronous replica with no noloadbalance tag. | is_replica=1;;@0\n"
    )


def test_node_is_replica_sync_ko(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    # We don't do the check ourselves, patroni does it and changes the return code
    result = runner.invoke(
        main, ["-e", patroni_api.endpoint, "node_is_replica", "--is-sync"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISREPLICA CRITICAL - This node is not a running synchronous replica with no noloadbalance tag. | is_replica=0;;@0\n"
    )


@pytest.mark.usefixtures("node_is_replica_ok")
def test_node_is_replica_async_ok(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    # We don't do the check ourselves, patroni does it and changes the return code
    result = runner.invoke(
        main, ["-e", patroni_api.endpoint, "node_is_replica", "--is-async"]
    )
    assert result.exit_code == 0
    assert (
        result.stdout
        == "NODEISREPLICA OK - This node is a running asynchronous replica with no noloadbalance tag. | is_replica=1;;@0\n"
    )


def test_node_is_replica_async_ko(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    # We don't do the check ourselves, patroni does it and changes the return code
    result = runner.invoke(
        main, ["-e", patroni_api.endpoint, "node_is_replica", "--is-async"]
    )
    assert result.exit_code == 2
    assert (
        result.stdout
        == "NODEISREPLICA CRITICAL - This node is not a running asynchronous replica with no noloadbalance tag. | is_replica=0;;@0\n"
    )


@pytest.mark.usefixtures("node_is_replica_ok")
def test_node_is_replica_params(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    # We don't do the check ourselves, patroni does it and changes the return code
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
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
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
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
