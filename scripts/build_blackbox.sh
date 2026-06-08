#!/usr/bin/env bash
# Build blackbox_decode from source (macOS / Linux)
# No library dependencies — only gcc/make required.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BLACKBOX_SRC="$PROJECT_ROOT/vendor/blackbox-tools"
BIN_DIR="$PROJECT_ROOT/bin"

echo "[build_blackbox] Source: $BLACKBOX_SRC"
echo "[build_blackbox] Output: $BIN_DIR"

# Sanity check — submodule populated?
if [ ! -f "$BLACKBOX_SRC/Makefile" ]; then
    echo "ERROR: vendor/blackbox-tools not found."
    echo "Run:  git submodule update --init --recursive"
    exit 1
fi

# Build only blackbox_decode (no cairo / libpng needed)
cd "$BLACKBOX_SRC"
make obj/blackbox_decode

# Copy to project bin/
mkdir -p "$BIN_DIR"
cp obj/blackbox_decode "$BIN_DIR/blackbox_decode"
chmod +x "$BIN_DIR/blackbox_decode"

echo "[build_blackbox] Done → $BIN_DIR/blackbox_decode"
