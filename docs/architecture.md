# Architecture

envdiff is a single stdlib-only module (`envdiff.py`). The flow is a straight
pipeline, no plugins or config files.

## Overview

```
source A ─┐
          ├─> parse to {key: value} ─> diff ─> mask secrets ─> render ─> exit code
source B ─┘
```

## Components

- **Source loaders** — one function per source kind, selected by prefix through
  the `SOURCE_LOADERS` table: `cmd:` (subprocess output), `k8s:ns/pod[/container]`
  (`kubectl exec ... -- env`), `docker:container` (`docker exec ... env`),
  `ssm:/path` and `secrets:name` (the `aws` CLI). A bare path is read as a file
  and `-` is read from stdin. Everything that shells out goes through `capture`,
  which runs the argv with no shell and raises on a non-zero exit.
- **Parser** — turns raw `KEY=VALUE` lines into a dict.
- **Differ** — computes added / removed / changed keys, honoring `--ignore`, and
  returns an `EnvDiff` record that also carries both sides for the summary line.
- **Masker** — replaces values whose key *looks* secret or whose value is
  high-entropy with a stable 6-char fingerprint plus a length/charset shape hint.
  On by default; `--no-mask` disables it.
- **Renderers** — `text` (the `+ / - / ~` diff), `markdown` (a table for a PR or
  ticket) and `json` (for scripting), selected by `--format`.

## Data flow

Each side is parsed independently and compared key by key. The renderers are the
only code that turns a value into output, and every one of them goes through the
masking callable it is handed, so a raw secret reaches stdout only under
`--no-mask`.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | the environments differ and `--fail-on-diff` was given |
| 2 | usage error from the argument parser |
| 65 | an `--ignore` value is not a valid regex |
| 66 | a source file or command could not be found |
| 69 | a source command ran and failed |

A CI gate can therefore tell drift (1) from a broken invocation (everything else).

## Decisions

- **Stdlib only** — no runtime dependencies, so it runs anywhere Python does.
- **Mask by default** — safe to paste output into a ticket; opt out explicitly.
- **Exit code as a gate** — `--fail-on-diff` makes it usable in CI.
