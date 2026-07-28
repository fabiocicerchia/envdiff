#!/usr/bin/env python3
"""envdiff — diff environment variables between two environments, safely.

Sources (auto-detected per argument):
  file.env                dotenv / `env` output / KEY=VALUE lines
  -                       stdin
  cmd:'ssh prod env'      output of a command
  k8s:ns/pod[/container]  env of a running pod (kubectl exec ... env)
  docker:container        env of a running container (docker exec ... env)
  ssm:/path/prefix        AWS SSM parameters under a path (aws ssm cli)
  secrets:name            AWS Secrets Manager secret (aws secretsmanager cli)

Secret-looking values (KEY matching token/secret/password/key/etc., or any
value that looks high-entropy) are masked by default: only a stable 6-char
fingerprint is shown, so you can tell "same secret" from "different secret"
without ever printing it.
"""

import argparse
import hashlib
import json
import math
import re
import shlex
import subprocess
import sys

SECRET_KEY_RE = re.compile(
    r"(secret|token|password|passwd|api_?key|private|credential|auth|cert|salt|dsn)",
    re.I,
)


def shannon_entropy(value):
    """Return the Shannon entropy (bits/char) of a string."""
    if not value:
        return 0.0
    freq = {c: value.count(c) for c in set(value)}
    return -sum((n / len(value)) * math.log2(n / len(value)) for n in freq.values())


def looks_secret(key, value):
    """True if a key name or its value looks like a credential."""
    if SECRET_KEY_RE.search(key):
        return True
    # long, high-entropy, no spaces → probably a credential
    return len(value) >= 16 and " " not in value and shannon_entropy(value) > 4.0


def fingerprint(value):
    """Return a stable 6-char hash so equal secrets compare equal."""
    return hashlib.sha256(value.encode()).hexdigest()[:6]


def charset_class(value):
    """Classify a string's charset as a shape hint, without revealing it."""
    if value.isdigit():
        return "numeric"
    if re.fullmatch(r"[0-9a-fA-F]+", value):
        return "hex"
    if value.isalnum():
        return "alnum"
    if re.fullmatch(r"[A-Za-z0-9+/]+=*", value):
        return "base64"
    return "mixed"


def mask(key, value, no_mask=False):
    """Replace secret-looking values with a fingerprint + shape hint unless no_mask."""
    if no_mask or not looks_secret(key, value):
        return value
    return (
        f"<masked:{fingerprint(value)} len={len(value)} charset={charset_class(value)}>"
    )


def parse_env_text(text):
    """Parse KEY=VALUE lines (dotenv / `env` output) into a dict."""
    env = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip().removeprefix("export ").strip()] = value.strip().strip("'\"")
    return env


def load(source):
    """Load an environment dict from a file, stdin, `cmd:` or `k8s:` source."""
    if source == "-":
        return parse_env_text(sys.stdin.read())
    if source.startswith("cmd:"):
        # ponytail: shlex.split + shell=False runs the user's command without a
        # shell interpreting metacharacters. For pipes, use cmd:sh -c '...'.
        out = subprocess.run(
            shlex.split(source[4:]),
            check=True,  # nosec B603
            capture_output=True,
            text=True,
        )
        return parse_env_text(out.stdout)
    if source.startswith("k8s:"):
        parts = source[4:].split("/")
        ns, pod = parts[0], parts[1]
        cmd = ["kubectl", "-n", ns, "exec", pod]
        if len(parts) > 2:
            cmd += ["-c", parts[2]]
        cmd += ["--", "env"]
        out = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )  # nosec B603
        return parse_env_text(out.stdout)
    if source.startswith("docker:"):
        out = subprocess.run(
            ["docker", "exec", source[7:], "env"],
            check=True,
            capture_output=True,
            text=True,
        )  # nosec B603
        return parse_env_text(out.stdout)
    if source.startswith("ssm:"):
        # aws ssm parameters-by-path, decrypted; last path segment is the key
        out = subprocess.run(
            [
                "aws",
                "ssm",
                "get-parameters-by-path",
                "--path",
                source[4:],
                "--recursive",
                "--with-decryption",
                "--output",
                "json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )  # nosec B603
        params = json.loads(out.stdout).get("Parameters", [])
        return {p["Name"].rsplit("/", 1)[-1]: p["Value"] for p in params}
    if source.startswith("secrets:"):
        name = source[8:]
        out = subprocess.run(
            [
                "aws",
                "secretsmanager",
                "get-secret-value",
                "--secret-id",
                name,
                "--output",
                "json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )  # nosec B603
        secret_string = json.loads(out.stdout).get("SecretString", "")
        try:
            # structured secret: {"KEY": "value", ...}
            return {k: str(v) for k, v in json.loads(secret_string).items()}
        except (ValueError, AttributeError):
            return {name: secret_string}
    with open(source) as fh:
        return parse_env_text(fh.read())


def diff(a, b, ignore=()):
    """Return (added, removed, changed) between env dicts a and b."""
    ignore_re = [re.compile(p) for p in ignore]

    def ignored(k):
        return any(r.fullmatch(k) for r in ignore_re)

    added = {k: b[k] for k in b.keys() - a.keys() if not ignored(k)}
    removed = {k: a[k] for k in a.keys() - b.keys() if not ignored(k)}
    changed = {
        k: (a[k], b[k]) for k in a.keys() & b.keys() if a[k] != b[k] and not ignored(k)
    }
    return added, removed, changed


def _total(added, removed, changed):
    return len(added) + len(removed) + len(changed)


def render_text(added, removed, changed, left, right, show):
    """Render the diff as the classic +/-/~ line format."""
    lines = [f"+ {k}={show(k, added[k])}" for k in sorted(added)]
    lines += [f"- {k}={show(k, removed[k])}" for k in sorted(removed)]
    lines += [
        f"~ {k}: {show(k, changed[k][0])} -> {show(k, changed[k][1])}"
        for k in sorted(changed)
    ]
    total = _total(added, removed, changed)
    lines.append("")
    lines.append(
        f"{total} difference(s): {len(added)} added, {len(removed)} removed, "
        f"{len(changed)} changed ({len(left)} vs {len(right)} vars)"
    )
    return "\n".join(lines)


def render_markdown(added, removed, changed, left, right, show):
    """Render the diff as a markdown table, safe to paste into a PR/ticket."""
    lines = ["| | Key | Value |", "|---|---|---|"]
    lines += [f"| + | `{k}` | `{show(k, added[k])}` |" for k in sorted(added)]
    lines += [f"| - | `{k}` | `{show(k, removed[k])}` |" for k in sorted(removed)]
    lines += [
        f"| ~ | `{k}` | `{show(k, changed[k][0])}` → `{show(k, changed[k][1])}` |"
        for k in sorted(changed)
    ]
    total = _total(added, removed, changed)
    lines.append("")
    lines.append(
        f"**{total} difference(s)**: {len(added)} added, {len(removed)} removed, "
        f"{len(changed)} changed ({len(left)} vs {len(right)} vars)"
    )
    return "\n".join(lines)


def render_json(added, removed, changed, left, right, show):
    """Render the diff as a JSON object, for scripting."""
    return json.dumps(
        {
            "added": {k: show(k, v) for k, v in added.items()},
            "removed": {k: show(k, v) for k, v in removed.items()},
            "changed": {
                k: {"old": show(k, old), "new": show(k, new)}
                for k, (old, new) in changed.items()
            },
            "summary": {
                "total": _total(added, removed, changed),
                "added": len(added),
                "removed": len(removed),
                "changed": len(changed),
                "left_vars": len(left),
                "right_vars": len(right),
            },
        },
        indent=2,
        sort_keys=True,
    )


RENDERERS = {"text": render_text, "json": render_json, "markdown": render_markdown}


def main(argv=None):
    """CLI entry point: parse args, diff the two environments, print results."""
    p = argparse.ArgumentParser(
        prog="envdiff",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("left", help="first environment (see sources above)")
    p.add_argument("right", help="second environment")
    p.add_argument(
        "--no-mask", action="store_true", help="print raw values (careful in CI logs!)"
    )
    p.add_argument(
        "--ignore",
        action="append",
        default=[],
        metavar="REGEX",
        help="ignore keys matching regex (repeatable)",
    )
    p.add_argument(
        "--fail-on-diff", action="store_true", help="exit 1 when environments differ"
    )
    p.add_argument(
        "--format",
        choices=sorted(RENDERERS),
        default="text",
        help="output format (default: text)",
    )
    args = p.parse_args(argv)

    left, right = load(args.left), load(args.right)
    added, removed, changed = diff(left, right, args.ignore)

    def show(k, v):
        return mask(k, v, args.no_mask)

    print(RENDERERS[args.format](added, removed, changed, left, right, show))

    total = _total(added, removed, changed)
    return 1 if (total and args.fail_on_diff) else 0


if __name__ == "__main__":
    sys.exit(main())
