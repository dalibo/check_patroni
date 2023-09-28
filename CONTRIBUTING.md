# Contributing to check_patroni

Thanks for your interest in contributing to check_patroni.

## Clone Git Repository

Installation from the git repository:

```
$ git clone https://github.com/dalibo/check_patroni.git
$ cd check_patroni
```

Change the branch if necessary.

## Create Python Virtual Environment

You need a dedicated environment, install dependencies and then check_patroni
from the repo:

```
$ python3 -m venv .venv
$ . .venv/bin/activate
(.venv) $ pip3 install .[test]
(.venv) $ pip3 install -r requirements-dev.txt
(.venv) $ check_patroni
```

To quit this env and destroy it:

```
$ deactivate
$ rm -r .venv
```

## Development Environment

A vagrant file is available to create a icinga / opm / grafana stack and
install check_patroni. You can then add a server to the supervision and
watch the graphs in grafana. It's in the `vagrant` directory.

A vagrant file can be found in [this
repository](https://github.com/ioguix/vagrant-patroni) to generate a patroni/etcd
setup.

The `README.md` can be generated with `./docs/make_readme.sh`.

## Executing Tests

Crafting repeatable tests using a live Patroni cluster can be intricate. To
simplify the development process, a fake HTTP server is set up as a test
fixture and serves static files (either from `tests/json` directory or from
in-memory data).

An important consideration is that there is a potential drawback: if the JSON
data is incorrect or if modifications have been made to Patroni without
corresponding updates to the tests documented here, the tests might still pass
erroneously.

The tests are executed automatically for each PR using the ci (see
`.github/workflow/lint.yml` and `.github/workflow/tests.yml`).

Running the tests,

* manually:

  ```bash
  pytest --cov tests
  ```

* or using tox:

  ```bash
  tox -e lint    # mypy + flake8 + black + isort ° codespell
  tox            # pytests and "lint" tests for all supported version of python
  tox -e py      # pytests and "lint" tests for the default version of python
  ```

Please note that when dealing with any service that checks the state of a node,
the related tests must use the `old_replica_state` fixture to test with both
old (pre 3.0.4) and new replica states.

A bash script, `check_patroni.sh`, is provided to facilitate testing all
services on a Patroni endpoint (`./vagrant/check_patroni.sh`). It requires one
parameter: the endpoint URL that will be used as the argument for the
`-e/--endpoints` option of `check_patroni`. This script essentially compiles a
list of service calls and executes them sequentially in a bash script. It
creates a state file in the directory from which you run the script.

Here's an example usage:

```bash
./vagrant/check_patroni.sh http://10.20.30.51:8008
```
