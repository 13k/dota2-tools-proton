#!/bin/bash

set -o errexit
set -o pipefail

SCRIPT_PATH="$(realpath "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
ROOT_DIR="$(realpath "${SCRIPT_DIR}/..")"

\cd "$ROOT_DIR"
\pwd
\poetry install
\poetry run pyinstaller -y -F --name="d2tp" "d2tp/__main__.py"
\cp "dist/d2tp" "${D2TP_BIN:?}"
\chmod 755 "$D2TP_BIN"
"$D2TP_BIN" --version
