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
repository](https://github.com/ioguix/vagrant-patroni to generate a patroni/etcd
setup.

The `README.md` can be geneated with `./docs/make_readme.sh`.


## Executing Tests

The pytests are in `./tests` and use a moker to provide a json response instead
of having to call the patroni API. To manually run the tests use one of these
commands :

```
pytest ./tests  # just the tests
tox             # pytests for all supported version of python + mypy + flake8
tox -e py       # pytests + mypy + flake8 or the default version of python
```

The tests are executed automatically for each PR using the ci (see
`.github/workflow/lint.yml` and `.github/workflow/tests.yml`).

## Release

The package is generated and uploaded to pypi when a `v*` tag is created (see
`.github/workflow/publish.yml`).

Alternatively, the release can be done manually with:

```
tox -e build
tox -e upload
```
