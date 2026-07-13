# Basic Example

What it shows: diffing two dotenv files, with secret-looking values masked.

## Run

```sh
envdiff staging.env prod.env
```

Expected output (fingerprints will differ on your machine):

```console
+ FEATURE_RETRY=true
- LEGACY_MODE=1
~ DB_PASSWORD: <masked:…> -> <masked:…>
~ LOG_LEVEL: debug -> info

4 difference(s): 1 added, 1 removed, 2 changed (5 vs 5 vars)
```

`DB_PASSWORD` is masked because its key looks like a secret — you can see the
two values *differ* without either being printed. Add `--no-mask` to reveal
them (avoid in CI logs).
