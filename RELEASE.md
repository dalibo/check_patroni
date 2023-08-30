# Release HOW TO

## Preparatory changes

* Review the **Unreleased** section, if any, in `CHANGELOG.md` possibly adding
  any missing item from closed issues, merged pull requests, or directly the
  git history[^git-changes],
* Rename the **Unreleased** section according to the version to be released,
  with a date,
* Bump the version in `check_patroni/__init__.py`,
* Rebuild the `README.md` (`cd docs; ./make_readme.sh`),
* Commit these changes (either on a dedicated branch, before submitting a pull
  request or directly on the `master` branch) with the commit message `release
  X.Y.Z`.
* Then, when changes landed in the `master` branch, create an annotated (and
  possibly signed) tag, as `git tag -a [-s] -m 'release X.Y.Z' vX.Y.Z`,
  and,
* Push with `--follow-tags`.

[^git-changes]: Use `git log $(git describe --tags --abbrev=0).. --format=%s
  --reverse` to get commits from the previous tag.

## PyPI package

The package is generated and uploaded to pypi when a `v*` tag is created (see
`.github/workflow/publish.yml`).

Alternatively, the release can be done manually with:

```
tox -e build
tox -e upload
```

## GitHub release

Draft a new release from the release page, choosing the tag just pushed and
copy the relevant change log section as a description.
