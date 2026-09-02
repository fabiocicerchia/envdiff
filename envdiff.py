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
import dataclasses
import functools
import hashlib
import json
import math
import re
import shlex
import subprocess
import sys

SECRET_KEY_RE = re.compile(
    r"(secret|token|password|passwd|api_?key|private|credential|auth|cert|salt|dsn)",
    re.IGNORECASE,
)
HEX_RE = re.compile(r"[0-9a-fA-F]+")
BASE64_RE = re.compile(r"[A-Za-z0-9+/]+=*")

# A value is treated as a credential on its shape alone once it is at least this
# long and this random; below either bound, English prose scores the same.
SECRET_MIN_LENGTH = 16
SECRET_MIN_ENTROPY_BITS = 4.0

# Exit codes, sysexits(3). 1 stays "the environments differ" — it is the
# documented --fail-on-diff CI gate — so every other failure gets its own code
# and a broken source can no longer be mistaken for drift. 2 is argparse's own.
EXIT_DIFF = 1
EXIT_DATAERR = 65  # an --ignore value is not a valid regex
EXIT_NOINPUT = 66  # a source file or command could not be found
EXIT_UNAVAILABLE = 69  # a source command ran and failed


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
    return (
        len(value) >= SECRET_MIN_LENGTH
        and " " not in value
        and shannon_entropy(value) > SECRET_MIN_ENTROPY_BITS
    )


def fingerprint(value):
    """Return a stable 6-char hash so equal secrets compare equal."""
    return hashlib.sha256(value.encode()).hexdigest()[:6]


def charset_class(value):
    """Classify a string's charset as a shape hint, without revealing it."""
    if value.isdigit():
        return "numeric"
    if HEX_RE.fullmatch(value):
        return "hex"
    if value.isalnum():
        return "alnum"
    if BASE64_RE.fullmatch(value):
        return "base64"
    return "mixed"


def mask(key, value, no_mask=False):
    """Replace secret-looking values with a fingerprint + shape hint unless no_mask."""
    if no_mask or not looks_secret(key, value):
        return value
    return f"<masked:{fingerprint(value)} len={len(value)} charset={charset_class(value)}>"


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


def capture(argv):
    """Run argv with no shell and return its stdout; raise if it exits non-zero.

    Every source that shells out goes through here: a copy that forgot
    check=True would read an empty environment as "every variable removed".
    """
    out = subprocess.run(argv, check=True, capture_output=True, text=True)  # nosec B603
    return out.stdout


def load_cmd(command):
    """Environment printed by an arbitrary command."""
    # ponytail: shlex.split + shell=False runs the user's command without a
    # shell interpreting metacharacters. For pipes, use cmd:sh -c '...'.
    return parse_env_text(capture(shlex.split(command)))


def load_k8s(target):
    """Environment of a running pod, addressed as ns/pod[/container]."""
    parts = target.split("/")
    argv = ["kubectl", "-n", parts[0], "exec", parts[1]]
    if len(parts) > 2:
        argv += ["-c", parts[2]]
    return parse_env_text(capture(argv + ["--", "env"]))


def load_docker(container):
    """Environment of a running container."""
    return parse_env_text(capture(["docker", "exec", container, "env"]))


def load_ssm(path):
    """AWS SSM parameters under a path, decrypted; last path segment is the key."""
    stdout = capture(
        [
            "aws",
            "ssm",
            "get-parameters-by-path",
            "--path",
            path,
            "--recursive",
            "--with-decryption",
            "--output",
            "json",
        ]
    )
    params = json.loads(stdout).get("Parameters", [])
    return {p["Name"].rsplit("/", 1)[-1]: p["Value"] for p in params}


def load_secrets(name):
    """An AWS Secrets Manager secret: a JSON object of vars, or one raw value."""
    stdout = capture(
        ["aws", "secretsmanager", "get-secret-value", "--secret-id", name, "--output", "json"]
    )
    secret_string = json.loads(stdout).get("SecretString", "")
    try:
        # structured secret: {"KEY": "value", ...}
        return {k: str(v) for k, v in json.loads(secret_string).items()}
    except (ValueError, AttributeError):
        return {name: secret_string}


SOURCE_LOADERS = {
    "cmd:": load_cmd,
    "k8s:": load_k8s,
    "docker:": load_docker,
    "ssm:": load_ssm,
    "secrets:": load_secrets,
}


def load(source):
    """Load an environment dict from a source argument (see the module docstring)."""
    if source == "-":
        return parse_env_text(sys.stdin.read())
    for prefix, loader in SOURCE_LOADERS.items():
        if source.startswith(prefix):
            return loader(source[len(prefix) :])
    with open(source) as fh:
        return parse_env_text(fh.read())


def ignored(key, ignore_res):
    """True if key matches any of the compiled --ignore patterns end to end."""
    return any(pattern.fullmatch(key) for pattern in ignore_res)


@dataclasses.dataclass(frozen=True)
class EnvDiff:
    """One comparison of two environments, as every renderer consumes it."""

    added: dict
    removed: dict
    changed: dict
    left: dict
    right: dict

    @property
    def total(self):
        """Number of keys that differ."""
        return len(self.added) + len(self.removed) + len(self.changed)


def diff(left, right, ignore=()):
    """Return the EnvDiff between the left and right env dicts."""
    ignore_res = [re.compile(pattern) for pattern in ignore]
    return EnvDiff(
        added={k: right[k] for k in right.keys() - left.keys() if not ignored(k, ignore_res)},
        removed={k: left[k] for k in left.keys() - right.keys() if not ignored(k, ignore_res)},
        changed={
            k: (left[k], right[k])
            for k in left.keys() & right.keys()
            if left[k] != right[k] and not ignored(k, ignore_res)
        },
        left=left,
        right=right,
    )


def render_text(result, show):
    """Render the diff as the classic +/-/~ line format."""
    added, removed, changed = result.added, result.removed, result.changed
    lines = [f"+ {k}={show(k, added[k])}" for k in sorted(added)]
    lines += [f"- {k}={show(k, removed[k])}" for k in sorted(removed)]
    lines += [
        f"~ {k}: {show(k, changed[k][0])} -> {show(k, changed[k][1])}" for k in sorted(changed)
    ]
    lines.append("")
    lines.append(
        f"{result.total} difference(s): {len(added)} added, {len(removed)} removed, "
        f"{len(changed)} changed ({len(result.left)} vs {len(result.right)} vars)"
    )
    return "\n".join(lines)


def render_markdown(result, show):
    """Render the diff as a markdown table, safe to paste into a PR/ticket."""
    added, removed, changed = result.added, result.removed, result.changed
    lines = ["| | Key | Value |", "|---|---|---|"]
    lines += [f"| + | `{k}` | `{show(k, added[k])}` |" for k in sorted(added)]
    lines += [f"| - | `{k}` | `{show(k, removed[k])}` |" for k in sorted(removed)]
    lines += [
        f"| ~ | `{k}` | `{show(k, changed[k][0])}` → `{show(k, changed[k][1])}` |"
        for k in sorted(changed)
    ]
    lines.append("")
    lines.append(
        f"**{result.total} difference(s)**: {len(added)} added, {len(removed)} removed, "
        f"{len(changed)} changed ({len(result.left)} vs {len(result.right)} vars)"
    )
    return "\n".join(lines)


def render_json(result, show):
    """Render the diff as a JSON object, for scripting."""
    return json.dumps(
        {
            "added": {k: show(k, v) for k, v in result.added.items()},
            "removed": {k: show(k, v) for k, v in result.removed.items()},
            "changed": {
                k: {"old": show(k, old), "new": show(k, new)}
                for k, (old, new) in result.changed.items()
            },
            "summary": {
                "total": result.total,
                "added": len(result.added),
                "removed": len(result.removed),
                "changed": len(result.changed),
                "left_vars": len(result.left),
                "right_vars": len(result.right),
            },
        },
        indent=2,
        sort_keys=True,
    )


RENDERERS = {"text": render_text, "json": render_json, "markdown": render_markdown}


def main(argv=None):
    """CLI entry point: parse args, diff the two environments, print results."""
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("left", help="first environment (see sources above)")
    parser.add_argument("right", help="second environment")
    parser.add_argument(
        "--no-mask", action="store_true", help="print raw values (careful in CI logs!)"
    )
    parser.add_argument(
        "--ignore",
        action="append",
        default=[],
        metavar="REGEX",
        help="ignore keys matching regex (repeatable)",
    )
    parser.add_argument(
        "--fail-on-diff", action="store_true", help="exit 1 when environments differ"
    )
    parser.add_argument(
        "--format",
        choices=sorted(RENDERERS),
        default="text",
        help="output format (default: text)",
    )
    args = parser.parse_args(argv)

    try:
        result = diff(load(args.left), load(args.right), args.ignore)
    except re.error as exc:
        print(f"envdiff: error: bad --ignore pattern: {exc}", file=sys.stderr)
        return EXIT_DATAERR
    except subprocess.CalledProcessError as exc:
        print(f"envdiff: error: source command exited {exc.returncode}", file=sys.stderr)
        return EXIT_UNAVAILABLE
    except OSError as exc:
        print(f"envdiff: error: {exc.filename}: {exc.strerror}", file=sys.stderr)
        return EXIT_NOINPUT

    show = functools.partial(mask, no_mask=args.no_mask)
    print(RENDERERS[args.format](result, show))
    return EXIT_DIFF if (result.total and args.fail_on_diff) else 0


if __name__ == "__main__":
    sys.exit(main())
