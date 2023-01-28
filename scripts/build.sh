#!/bin/bash

set -o errexit
set -o pipefail

SCRIPT_PATH="$(realpath "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"
pwd

poetry install
poetry run pyinstaller "d2tp.spec"

cp "dist/d2tp" "${D2TP_BIN:?}"
chmod 755 "$D2TP_BIN"

"$D2TP_BIN" --version
