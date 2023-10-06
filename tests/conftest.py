import sys
from pathlib import Path
from threading import Thread
from typing import Any, Iterator, Tuple

if sys.version_info >= (3, 8):
    from importlib.metadata import version as metadata_version
else:
    from importlib_metadata import version as metadata_version

import pytest
from click.testing import CliRunner

from . import PatroniAPI


def numversion(pkgname: str) -> Tuple[int, ...]:
    version = metadata_version(pkgname)
    return tuple(int(v) for v in version.split(".", 3))


if numversion("pytest") >= (6, 2):
    TempPathFactory = pytest.TempPathFactory
else:
    from _pytest.tmpdir import TempPathFactory


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
    tmp_path_factory: TempPathFactory, datadir: Path
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
