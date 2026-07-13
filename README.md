# envdiff

[![CI](https://github.com/fabiocicerchia/envdiff/actions/workflows/ci.yml/badge.svg)](https://github.com/fabiocicerchia/envdiff/actions/workflows/ci.yml)
[![Security](https://github.com/fabiocicerchia/envdiff/actions/workflows/security.yml/badge.svg)](https://github.com/fabiocicerchia/envdiff/actions/workflows/security.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/fabiocicerchia/envdiff/badge)](https://securityscorecards.dev/viewer/?uri=github.com/fabiocicerchia/envdiff)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Diff environment variables **between two running environments** with
**secret masking on by default**. "Why does it work in staging but not in
prod?" — answered in one command, safe to paste into a ticket.

```console
$ envdiff k8s:staging/api-7d9f k8s:prod/api-5c2a --ignore 'HOSTNAME|POD_.*'
+ FEATURE_RETRY=true
- LEGACY_MODE=1
~ DB_PASSWORD: <masked:9f2c1a> -> <masked:4b8e77>
~ LOG_LEVEL: debug -> info

4 difference(s): 1 added, 1 removed, 2 changed (41 vs 41 vars)
```

Secrets are never printed: values with secret-looking keys *or* high-entropy
values are replaced by a stable 6-char fingerprint — enough to see *whether*
two environments share the same secret, without revealing it.

## Sources

| Argument | Meaning |
|---|---|
| `file.env` | dotenv file / captured `env` output |
| `-` | stdin |
| `cmd:'ssh prod env'` | output of any command |
| `k8s:ns/pod[/container]` | live pod env via `kubectl exec` |

## Install & use

```sh
pipx install .
envdiff .env.staging .env.prod
envdiff cmd:'heroku run env -a app-stg' cmd:'heroku run env -a app-prd'
envdiff a.env b.env --fail-on-diff        # CI drift gate (exit 1 on diff)
envdiff a.env b.env --no-mask             # only when you really mean it
```

## Roadmap

- [ ] `docker:container` source, AWS SSM / Secrets Manager sources
- [ ] JSON/markdown output
- [ ] Value-shape hints for masked diffs (length, charset)

## Development

`make dev` then `make test` / `make lint`. Deeper docs live in [`docs/`](docs/),
runnable examples in [`examples/`](examples/).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). By participating you agree to the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) — please don't open a
public issue.

## License

Apache 2.0 — see [LICENSE](LICENSE).
