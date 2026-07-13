# Contributing

Thanks for taking the time to contribute to envdiff! By participating you agree
to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Development setup

You need Python 3.10+ and `make`.

```sh
make setup   # git hooks + pre-commit (secret scanning, ruff)
make dev     # editable install with dev dependencies (pytest, ruff, build)
make lint    # ruff check .
make test    # pytest
```

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`,
`fix:`, `docs:`, `chore:`, etc. They drive the version bump — `fix:` → patch,
`feat:` → minor, `feat!:` or a `BREAKING CHANGE:` footer → major — and generate
`CHANGELOG.md`, so **don't edit the changelog by hand**.

## Pull requests

1. Fork and create a topic branch.
1. Make your change, keeping the existing style; add or update tests.
1. Make sure `make lint` and `make test` pass locally.
1. Open a PR with a clear description of the problem and the solution.

## Releases

Automated by [release-please](.github/workflows/release.yml): you don't tag or
edit the changelog manually.

1. Merge `feat:`/`fix:` PRs into `main` — **no tag is created**.
1. release-please keeps an open **release PR** ("chore: release X.Y.Z"),
   recalculating the next version and changelog on every merge.
1. When you're ready to ship, **merge the release PR** — that (and only that)
   bumps `pyproject.toml`, creates the `vX.Y.Z` tag and GitHub Release, and (if
   `PUBLISH_TO_PYPI` is set) publishes to PyPI.

## License

By contributing you agree that your contributions are licensed under the
Apache License 2.0 (see `LICENSE`).
