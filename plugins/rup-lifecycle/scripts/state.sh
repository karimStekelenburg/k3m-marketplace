#!/usr/bin/env bash
# state.sh — Read/write RUP cycle state from .claude/rup-state.json
# Usage:
#   state.sh get [field]           — Read full state or a specific field
#   state.sh set field value       — Set a top-level field
#   state.sh artifact name status [path] — Update artifact status
#   state.sh gate-record phase result [notes] — Record a gate evaluation
#   state.sh exists                — Check if state file exists (exit 0/1)

set -euo pipefail

STATE_DIR=".claude"
STATE_FILE="${STATE_DIR}/rup-state.json"

cmd_exists() {
  [[ -f "$STATE_FILE" ]]
}

cmd_get() {
  if ! cmd_exists; then
    echo '{"error": "No active cycle. Run /rup-init to start one."}' >&2
    exit 1
  fi

  if [[ $# -eq 0 ]]; then
    cat "$STATE_FILE"
  else
    local field="$1"
    jq -r ".$field // empty" "$STATE_FILE"
  fi
}

cmd_set() {
  if ! cmd_exists; then
    echo "Error: No active cycle." >&2
    exit 1
  fi

  local field="$1"
  local value="$2"

  # Detect if value is a number or JSON
  if echo "$value" | jq -e . >/dev/null 2>&1; then
    jq --argjson v "$value" ".$field = \$v" "$STATE_FILE" > "${STATE_FILE}.tmp"
  else
    jq --arg v "$value" ".$field = \$v" "$STATE_FILE" > "${STATE_FILE}.tmp"
  fi
  mv "${STATE_FILE}.tmp" "$STATE_FILE"
}

cmd_artifact() {
  if ! cmd_exists; then
    echo "Error: No active cycle." >&2
    exit 1
  fi

  local name="$1"
  local status="$2"
  local path="${3:-}"

  if [[ -n "$path" ]]; then
    jq --arg n "$name" --arg s "$status" --arg p "$path" \
      '.artifacts[$n] = {"status": $s, "path": $p}' "$STATE_FILE" > "${STATE_FILE}.tmp"
  else
    jq --arg n "$name" --arg s "$status" \
      '.artifacts[$n].status = $s' "$STATE_FILE" > "${STATE_FILE}.tmp"
  fi
  mv "${STATE_FILE}.tmp" "$STATE_FILE"
}

cmd_gate_record() {
  local phase="$1"
  local result="$2"
  local notes="${3:-}"
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  jq --arg p "$phase" --arg r "$result" --arg n "$notes" --arg t "$timestamp" \
    '.gate_history += [{"phase": $p, "result": $r, "notes": $n, "timestamp": $t}]' \
    "$STATE_FILE" > "${STATE_FILE}.tmp"
  mv "${STATE_FILE}.tmp" "$STATE_FILE"
}

# Main dispatch
case "${1:-}" in
  exists)  cmd_exists ;;
  get)     shift; cmd_get "$@" ;;
  set)     shift; cmd_set "$@" ;;
  artifact) shift; cmd_artifact "$@" ;;
  gate-record) shift; cmd_gate_record "$@" ;;
  *)
    echo "Usage: state.sh {exists|get|set|artifact|gate-record} [args...]" >&2
    exit 1
    ;;
esac
