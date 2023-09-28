from functools import partial
from typing import Any, Callable

import pytest
from pytest_mock import MockerFixture

from .tools import my_mock


def pytest_addoption(parser: Any) -> None:
    """
    Add CLI options to `pytest` to pass those options to the test cases.
    These options are used in `pytest_generate_tests`.
    """
    parser.addoption("--use-old-replica-state", action="store_true", default=False)


def pytest_generate_tests(metafunc: Any) -> None:
    metafunc.parametrize(
        "use_old_replica_state", [metafunc.config.getoption("use_old_replica_state")]
    )


@pytest.fixture
def fake_restapi(
    mocker: MockerFixture, use_old_replica_state: bool
) -> Callable[..., Any]:
    return partial(my_mock, mocker, use_old_replica_state=use_old_replica_state)
