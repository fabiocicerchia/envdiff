# CLAUDE.md

Guidance for Claude Code (and other AI agents) working in this repo.

## Project

envdiff is a single-file Python 3.10+ CLI (`envdiff.py`) that diffs environment
variables between two running environments, masking secrets by default. Sources
are dotenv files, stdin (`-`), `cmd:'...'` output, or `k8s:ns/pod[/container]`
(via `kubectl exec`). Entry point: `envdiff:main` (see `pyproject.toml`).

## Commands

```sh
# setup: make dev        # editable install with dev deps (pytest, ruff, build)
# test:  make test       # pytest -q
# lint:  make lint        # ruff check .
# build: make build      # python -m build
# run:   envdiff a.env b.env
make help    # Show this help
make setup   # Install the pre-commit hook
make install # Install the package
make dev     # Editable install with dev dependencies
make lint    # Run ruff
make test    # Run tests
make build   # Build sdist and wheel
```

## Tooling

Shared config — the GitHub workflows, `.pre-commit-config.yaml`,
`.editorconfig`, `.hadolint.yaml`, `SECURITY.md` — comes from
[repo-skeleton](https://github.com/fabiocicerchia/repo-skeleton). Edit it
there, not here; a local edit is drift and the next sync overwrites it.
`check-drift.sh` in that repo reports what has diverged.

- `make setup` installs the pre-commit hook, and that is the whole of it.
  Don't add a `.githooks/` directory: `core.hooksPath` replaces `.git/hooks/`
  wholesale, so setting it silently stops every pre-commit hook from running.
- Hooks are pinned by commit SHA with the tag in a trailing comment. A tag can
  be moved, a SHA cannot.
- CI runs this same `.pre-commit-config.yaml` through `pre-commit/action`, so
  what passes locally is what gates the pull request.

## Conventions

- Match existing style; don't reformat unrelated code.
- Use [Conventional Commits](https://www.conventionalcommits.org/) — they drive
  the version bump and the auto-generated `CHANGELOG.md`. Don't edit the
  changelog by hand.
- Update `docs/` and `examples/` with behavior changes.
- Never commit secrets; CI runs gitleaks. Keep `.env` out of git.
- Secret masking is the core safety property — never print raw secret values;
  route through the existing masking helper.

## Guardrails

- Don't add dependencies without a clear reason; envdiff is stdlib-only by design.
- Don't touch generated files or lockfiles by hand.
- Ask before large refactors or destructive operations.

## Releases

Automated by release-please (see `.github/workflows/release.yml`): Conventional
Commits on `main` accumulate into an open release PR; merging it bumps
`pyproject.toml`, tags `vX.Y.Z`, and cuts the GitHub Release. No manual tags.
