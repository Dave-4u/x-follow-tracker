#!/usr/bin/env bash
# ./run.sh            -> Follow Ledger dashboard on http://127.0.0.1:8770 (reads data/, no cookies)
# ./run.sh run        -> fetch your lists once (needs AUTH_TOKEN + CT0 in .env)
# ./run.sh scan|watch -> other tracker commands
# ./run.sh test       -> test suite
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt -r requirements-dev.txt
  .venv/bin/python scripts/apply_twikit_patch.py
fi
case "${1:-dashboard}" in
  test) exec .venv/bin/python -m pytest -q ;;
  dashboard) exec .venv/bin/python -m follow_tracker dashboard --port "${PORT:-8770}" ;;
  *) exec .venv/bin/python -m follow_tracker "$@" ;;
esac
