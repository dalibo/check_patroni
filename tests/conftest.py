def pytest_addoption(parser):
    """
    Add CLI options to `pytest` to pass those options to the test cases.
    These options are used in `pytest_generate_tests`.
    """
    parser.addoption("--use-old-replica-state", action="store_true", default=False)


def pytest_generate_tests(metafunc):
    metafunc.parametrize(
        "use_old_replica_state", [metafunc.config.getoption("use_old_replica_state")]
    )
