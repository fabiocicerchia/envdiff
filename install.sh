#!/usr/bin/env bash
set -euo pipefail
# One-line installer for envdiff
# Usage: curl -fsSL https://raw.githubusercontent.com/fabiocicerchia/envdiff/main/install.sh | bash

if command -v pipx &>/dev/null; then
  pipx install git+https://github.com/fabiocicerchia/envdiff
else
  pip install --user git+https://github.com/fabiocicerchia/envdiff
fi
echo "envdiff installed. Run: envdiff --help"
