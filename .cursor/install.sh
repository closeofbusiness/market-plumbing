#!/usr/bin/env bash
# Idempotent bootstrap for the market-plumbing research environment.
# Safe to run repeatedly: it installs the venv system package if missing,
# (re)creates the virtualenv only when absent, and syncs pinned dependencies.
set -euo pipefail

cd "$(dirname "$0")/.."

# python3 venv support is a stable system dependency and ships separately on
# Debian/Ubuntu. Install it once if the ensurepip-backed venv module is broken.
if ! python3 -c "import ensurepip" >/dev/null 2>&1; then
  echo "Installing python3-venv system package ..."
  sudo apt-get update -qq
  sudo apt-get install -y -qq python3.12-venv
fi

if [ ! -x .venv/bin/python ]; then
  echo "Creating virtualenv at .venv ..."
  python3 -m venv .venv
fi

echo "Installing pinned dependencies ..."
.venv/bin/python -m pip install --upgrade pip >/dev/null
.venv/bin/pip install -r requirements.txt

echo "Environment ready. Activate with: source .venv/bin/activate"
