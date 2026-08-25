# Getting Started

## Prerequisites

- Python 3.10+
- `kubectl` on your PATH (only if you use `k8s:` sources)

## Install

```sh
pipx install .      # or: pip install .
```

## First diff

```sh
# two dotenv files
envdiff .env.staging .env.prod

# stdin and a command
kubectl exec pod -- env | envdiff - cmd:'ssh prod env'

# live pods, ignoring noisy keys
envdiff k8s:staging/api-7d9f k8s:prod/api-5c2a --ignore 'HOSTNAME|POD_.*'
```

Secrets are masked by default — values are shown as a stable `<masked:xxxxxx>`
fingerprint so you can compare *whether* two environments share a secret
without revealing it.

## CI drift gate

```sh
envdiff a.env b.env --fail-on-diff   # exit 1 when environments differ
```

See the top-level [README](README.md) for the full source syntax and flags.
