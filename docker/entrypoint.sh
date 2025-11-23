#!/usr/bin/env bash
set -euo pipefail

CMD=${1:-}
shift || true

case "$CMD" in
  run)
    exec python /app/src/run_once.py "$@"
    ;;
  schedule)
    exec python /app/src/run_scheduler.py "$@"
    ;;
  *)
    echo "Usage: entrypoint.sh [run|schedule]" >&2
    exit 1
    ;;
esac
