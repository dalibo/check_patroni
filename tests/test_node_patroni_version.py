from typing import Iterator

import pytest
from click.testing import CliRunner

from check_patroni.cli import main

from . import PatroniAPI


@pytest.fixture(scope="module", autouse=True)
def node_patroni_version(patroni_api: PatroniAPI) -> Iterator[None]:
    with patroni_api.routes({"patroni": "node_patroni_version.json"}):
        yield None


def test_node_patroni_version_ok(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
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


def test_node_patroni_version_ko(runner: CliRunner, patroni_api: PatroniAPI) -> None:
    result = runner.invoke(
        main,
        [
            "-e",
            patroni_api.endpoint,
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
