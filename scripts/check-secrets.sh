#!/usr/bin/env bash
set -euo pipefail

if command -v gitleaks >/dev/null 2>&1; then
  exec gitleaks git --redact --no-banner
fi

echo "gitleaks is required for the authoritative secret scan" >&2
exit 127
