#!/usr/bin/env bash
# Detect which backend to use for k3m-cycles.
# Priority: K3M_BACKEND env var > GitHub Actions detection > config file > default (fs)
#
# Usage: source this file, then use $K3M_BACKEND
#   source "$CLAUDE_PLUGIN_ROOT/scripts/detect-backend.sh"

set -euo pipefail

if [[ -n "${K3M_BACKEND:-}" ]]; then
  # Explicit override — respect it
  :
elif [[ "${GITHUB_ACTIONS:-}" == "true" ]]; then
  export K3M_BACKEND="github"
elif [[ -f ".k3m-cycles.json" ]]; then
  K3M_BACKEND=$(python3 -c "import json; print(json.load(open('.k3m-cycles.json')).get('backend', 'fs'))" 2>/dev/null || echo "fs")
  export K3M_BACKEND
else
  export K3M_BACKEND="fs"
fi

# Export helper paths
export K3M_SCRIPTS="${CLAUDE_PLUGIN_ROOT}/scripts"
export K3M_BACKEND_SCRIPT="${K3M_SCRIPTS}/backend-${K3M_BACKEND}.sh"

if [[ ! -f "$K3M_BACKEND_SCRIPT" ]]; then
  echo "ERROR: Unknown backend '$K3M_BACKEND' — no script at $K3M_BACKEND_SCRIPT" >&2
  exit 1
fi
