#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/judge.log"

while true; do
  echo "[START $(date --rfc-3339=seconds)] Running judge_agent" >> "$LOG_FILE"
  if (cd "$ROOT" && .venv/bin/python scripts/judge_agent.py >> "$LOG_FILE" 2>&1); then
    echo "[END $(date --rfc-3339=seconds)] judge_agent succeeded" >> "$LOG_FILE"
    exit 0
  fi
  echo "[FAIL $(date --rfc-3339=seconds)] judge_agent failed, retrying in 120s" >> "$LOG_FILE"
  sleep 120
done
