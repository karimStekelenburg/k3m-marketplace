#!/usr/bin/env bash
# validate-gate.sh — Check whether exit criteria are met for a phase gate
# Usage: validate-gate.sh [phase]
# If phase is omitted, reads current phase from state file.
# Exit code 0 = gate passed, 1 = gate failed
# Output: JSON with pass/fail details

set -euo pipefail

STATE_FILE=".claude/rup-state.json"

if [[ ! -f "$STATE_FILE" ]]; then
  echo '{"passed": false, "error": "No active cycle"}'
  exit 1
fi

PHASE="${1:-$(jq -r '.phase' "$STATE_FILE")}"
CYCLE_TYPE=$(jq -r '.cycle_type' "$STATE_FILE")

# Helper: check artifact status
check_artifact() {
  local name="$1"
  local required_status="$2"
  local actual_status
  local path

  actual_status=$(jq -r ".artifacts[\"$name\"].status // \"missing\"" "$STATE_FILE")
  path=$(jq -r ".artifacts[\"$name\"].path // \"\"" "$STATE_FILE")

  local file_exists="false"
  if [[ -n "$path" && -f "$path" ]]; then
    file_exists="true"
  fi

  local passed="false"
  case "$required_status" in
    "exists")
      # Just needs to exist as a file with non-pending status
      [[ "$file_exists" == "true" && "$actual_status" != "pending" ]] && passed="true"
      ;;
    "approved")
      [[ "$actual_status" == "approved" && "$file_exists" == "true" ]] && passed="true"
      ;;
    "draft")
      [[ ("$actual_status" == "draft" || "$actual_status" == "review" || "$actual_status" == "approved") && "$file_exists" == "true" ]] && passed="true"
      ;;
    *)
      [[ "$actual_status" == "$required_status" ]] && passed="true"
      ;;
  esac

  echo "{\"name\": \"$name\", \"required\": \"$required_status\", \"actual\": \"$actual_status\", \"file_exists\": $file_exists, \"passed\": $passed}"
}

# Define gate criteria per phase
results=()
all_passed=true

case "$PHASE" in
  inception)
    # INC → ELB: Vision approved, risk list drafted, initial requirements
    for check in \
      "vision:approved" \
      "risk-list:draft"; do
      name="${check%%:*}"
      req="${check#*:}"
      result=$(check_artifact "$name" "$req")
      results+=("$result")
      if echo "$result" | jq -e '.passed == false' >/dev/null; then
        all_passed=false
      fi
    done
    next_phase="elaboration"
    ;;

  elaboration)
    # ELB → CON: Requirements, architecture, dev-plan approved; risk list updated
    for check in \
      "vision:approved" \
      "requirements:approved" \
      "architecture:approved" \
      "dev-plan:approved" \
      "risk-list:approved"; do
      name="${check%%:*}"
      req="${check#*:}"
      result=$(check_artifact "$name" "$req")
      results+=("$result")
      if echo "$result" | jq -e '.passed == false' >/dev/null; then
        all_passed=false
      fi
    done
    next_phase="construction"
    ;;

  construction)
    # CON → TRN: Build plan exists, iteration assessments done
    for check in \
      "build-plan:approved"; do
      name="${check%%:*}"
      req="${check#*:}"
      result=$(check_artifact "$name" "$req")
      results+=("$result")
      if echo "$result" | jq -e '.passed == false' >/dev/null; then
        all_passed=false
      fi
    done
    # Check for iteration assessment files
    iteration_dir="artifacts/construction"
    iteration_count=$(find "$iteration_dir" -name "assessment.md" -type f 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$iteration_count" -eq 0 ]]; then
      results+=("{\"name\": \"iteration-assessments\", \"required\": \"at least 1\", \"actual\": \"$iteration_count found\", \"file_exists\": false, \"passed\": false}")
      all_passed=false
    else
      results+=("{\"name\": \"iteration-assessments\", \"required\": \"at least 1\", \"actual\": \"$iteration_count found\", \"file_exists\": true, \"passed\": true}")
    fi
    next_phase="transition"
    ;;

  transition)
    # TRN → Done: Release notes exist
    for check in \
      "release:approved"; do
      name="${check%%:*}"
      req="${check#*:}"
      result=$(check_artifact "$name" "$req")
      results+=("$result")
      if echo "$result" | jq -e '.passed == false' >/dev/null; then
        all_passed=false
      fi
    done
    next_phase="done"
    ;;

  *)
    echo "{\"passed\": false, \"error\": \"Unknown phase: $PHASE\"}"
    exit 1
    ;;
esac

# Build JSON output
checks_json=$(printf '%s\n' "${results[@]}" | jq -s '.')
cat <<EOF
{
  "phase": "$PHASE",
  "next_phase": "$next_phase",
  "cycle_type": "$CYCLE_TYPE",
  "passed": $all_passed,
  "checks": $checks_json
}
EOF

if [[ "$all_passed" == "true" ]]; then
  exit 0
else
  exit 1
fi
