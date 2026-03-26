#!/usr/bin/env bash
# init-cycle.sh — Bootstrap a new RUP development cycle
# Usage: init-cycle.sh <cycle_type>
# cycle_type: initial | evolution | maintenance

set -euo pipefail

CYCLE_TYPE="${1:-}"
STATE_DIR=".claude"
STATE_FILE="${STATE_DIR}/rup-state.json"
ARTIFACTS_DIR="artifacts"

if [[ -z "$CYCLE_TYPE" ]]; then
  echo "Usage: init-cycle.sh <cycle_type>"
  echo "  cycle_type: initial | evolution | maintenance"
  exit 1
fi

# Validate cycle type
case "$CYCLE_TYPE" in
  initial|evolution|maintenance) ;;
  *)
    echo "Error: Invalid cycle type '$CYCLE_TYPE'. Must be: initial, evolution, maintenance"
    exit 1
    ;;
esac

# Check for existing cycle
if [[ -f "$STATE_FILE" ]]; then
  current_phase=$(jq -r '.phase' "$STATE_FILE" 2>/dev/null || echo "unknown")
  echo "Warning: Active cycle exists (phase: $current_phase)."
  echo "State file: $STATE_FILE"
  echo "To start a new cycle, archive or remove the existing state file first."
  exit 1
fi

# Create state directory
mkdir -p "$STATE_DIR"

# Create artifact directory structure
mkdir -p "${ARTIFACTS_DIR}/inception"
mkdir -p "${ARTIFACTS_DIR}/elaboration"
mkdir -p "${ARTIFACTS_DIR}/construction"
mkdir -p "${ARTIFACTS_DIR}/transition"

# Define initial artifacts based on cycle type
# All cycles get the full set — gate criteria determine what's required per phase
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$STATE_FILE" <<EOF
{
  "cycle_type": "${CYCLE_TYPE}",
  "phase": "inception",
  "iteration": 1,
  "started": "${TIMESTAMP}",
  "artifacts": {
    "vision": {"status": "pending", "path": "artifacts/inception/vision.md"},
    "risk-list": {"status": "pending", "path": "artifacts/inception/risk-list.md"},
    "requirements": {"status": "pending", "path": "artifacts/elaboration/requirements.md"},
    "architecture": {"status": "pending", "path": "artifacts/elaboration/architecture.md"},
    "dev-plan": {"status": "pending", "path": "artifacts/elaboration/dev-plan.md"},
    "build-plan": {"status": "pending", "path": "artifacts/construction/build-plan.md"},
    "release": {"status": "pending", "path": "artifacts/transition/release.md"}
  },
  "gate_history": []
}
EOF

echo "Cycle initialized:"
echo "  Type:  $CYCLE_TYPE"
echo "  Phase: inception"
echo "  State: $STATE_FILE"
echo "  Artifacts: $ARTIFACTS_DIR/"
echo ""
echo "Directory structure created:"
find "$ARTIFACTS_DIR" -type d | sort | sed 's/^/  /'
