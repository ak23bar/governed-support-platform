#!/usr/bin/env bash
set -euo pipefail

task_venv="${VENV:-.venv}"
task_api_log="${TMPDIR:-/tmp}/gps-e01-api.log"
"${task_venv}/bin/pytest" -q
"${task_venv}/bin/uvicorn" apps.api.main:app --host 127.0.0.1 --port 8765 >"${task_api_log}" 2>&1 &
task_api_pid=$!
trap 'kill "${task_api_pid}" 2>/dev/null || true' EXIT

for task_attempt in 1 2 3 4 5; do
  if "${task_venv}/bin/python" - <<'PY'
import json
from urllib.request import urlopen

with urlopen("http://127.0.0.1:8765/health", timeout=1) as response:
    payload = json.load(response)
assert payload["status"] == "ok"
PY
  then
    exit 0
  fi
  if ! kill -0 "${task_api_pid}" 2>/dev/null; then
    echo "API process exited before becoming healthy; log follows:" >&2
    sed -n '1,240p' "${task_api_log}" >&2
    exit 1
  fi
  sleep "0.${task_attempt}"
done

echo "API health smoke test failed after bounded retries; log follows:" >&2
sed -n '1,240p' "${task_api_log}" >&2
exit 1
