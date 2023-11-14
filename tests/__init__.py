import json
import logging
import shutil
from contextlib import contextmanager
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Iterator, Mapping, Union

logger = logging.getLogger(__name__)


class PatroniAPI(HTTPServer):
    def __init__(self, directory: Path, *, datadir: Path) -> None:
        self.directory = directory
        self.datadir = datadir
        handler_cls = partial(SimpleHTTPRequestHandler, directory=str(directory))
        super().__init__(("", 0), handler_cls)

    def serve_forever(self, *args: Any) -> None:
        logger.info(
            "starting fake Patroni API at %s (directory=%s)",
            self.endpoint,
            self.directory,
        )
        return super().serve_forever(*args)

    @property
    def endpoint(self) -> str:
        return f"http://{self.server_name}:{self.server_port}"

    @contextmanager
    def routes(self, mapping: Mapping[str, Union[Path, str]]) -> Iterator[None]:
        """Temporarily install specified files in served directory, thus
        building "routes" from given mapping.

        The 'mapping' defines target route paths as keys and files to be
        installed in served directory as values. Mapping values of type 'str'
        are assumed be relative file path to the 'datadir'.
        """
        for route_path, fpath in mapping.items():
            if isinstance(fpath, str):
                fpath = self.datadir / fpath
            shutil.copy(fpath, self.directory / route_path)
        try:
            yield None
        finally:
            for fname in mapping:
                (self.directory / fname).unlink()


def cluster_api_set_replica_running(in_json: Path, target_dir: Path) -> Path:
    # starting from 3.0.4 the state of replicas is streaming or in archive recovery
    # instead of running
    with in_json.open() as f:
        js = json.load(f)
    for node in js["members"]:
        if node["role"] in ["replica", "sync_standby", "standby_leader"]:
            if node["state"] in ["streaming", "in archive recovery"]:
                node["state"] = "running"
    assert target_dir.is_dir()
    out_json = target_dir / in_json.name
    with out_json.open("w") as f:
        json.dump(js, f)
    return out_json
