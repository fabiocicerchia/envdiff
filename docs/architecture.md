# Architecture

envdiff is a single stdlib-only module (`envdiff.py`). The flow is a straight
pipeline, no plugins or config files.

## Overview

```
source A ─┐
          ├─> parse to {key: value} ─> mask secrets ─> diff ─> render ─> exit code
source B ─┘
```

## Components

- **Source loader** — resolves a source argument to raw text:
  `file.env`, `-` (stdin), `cmd:'...'` (subprocess output),
  `k8s:ns/pod[/container]` (`kubectl exec ... -- env`).
- **Parser** — turns raw `KEY=VALUE` lines into a dict.
- **Masker** — replaces values whose key *looks* secret or whose value is
  high-entropy with a stable 6-char fingerprint. On by default; `--no-mask`
  disables it.
- **Differ** — computes added / removed / changed keys, honoring `--ignore`.
- **Renderer** — prints the `+ / - / ~` diff and a summary line.

## Data flow

Each side is parsed and masked independently, then compared key-by-key. Masking
happens *before* diffing so raw secrets never reach the renderer.

## Decisions

- **Stdlib only** — no runtime dependencies, so it runs anywhere Python does.
- **Mask by default** — safe to paste output into a ticket; opt out explicitly.
- **Exit code as a gate** — `--fail-on-diff` makes it usable in CI.
