from functools import partial
from typing import Any, Callable

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from .tools import my_mock


@pytest.fixture(
    params=[False, True],
    ids=lambda v: "new-replica-state" if v else "old-replica-state",
)
def old_replica_state(request: Any) -> Any:
    return request.param


@pytest.fixture
def fake_restapi(mocker: MockerFixture) -> Callable[..., Any]:
    return partial(my_mock, mocker)


@pytest.fixture
def runner() -> CliRunner:
    """A CliRunner with stdout and stderr not mixed."""
    return CliRunner(mix_stderr=False)
