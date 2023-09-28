from pathlib import Path
from threading import Thread
from typing import Any, Iterator

import pytest
from click.testing import CliRunner

from . import PatroniAPI


@pytest.fixture(
    params=[False, True],
    ids=lambda v: "new-replica-state" if v else "old-replica-state",
)
def old_replica_state(request: Any) -> Any:
    return request.param


@pytest.fixture(scope="session")
def datadir() -> Path:
    return Path(__file__).parent / "json"


@pytest.fixture(scope="session")
def patroni_api(
    tmp_path_factory: pytest.TempPathFactory, datadir: Path
) -> Iterator[PatroniAPI]:
    """A fake HTTP server for the Patroni API serving files from a temporary
    directory.
    """
    httpd = PatroniAPI(tmp_path_factory.mktemp("api"), datadir=datadir)
    t = Thread(target=httpd.serve_forever)
    t.start()
    yield httpd
    httpd.shutdown()
    t.join()


@pytest.fixture
def runner() -> CliRunner:
    """A CliRunner with stdout and stderr not mixed."""
    return CliRunner(mix_stderr=False)
