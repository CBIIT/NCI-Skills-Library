#!/usr/bin/env bash
# cws_pm — porter: runs the Python orchestrator core (reads its inputs from the environment).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$HERE/cws_pm.py"
