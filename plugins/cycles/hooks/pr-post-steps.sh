#!/usr/bin/env bash
# PostToolUse hook for PR creation.
# After a PR is created during a cycle, enforce remaining steps.
set -euo pipefail

cat >&2 <<'EOF'
PR created. REQUIRED NEXT STEPS:
1) Run /spec-status to confirm summary.complete: true
2) Run Phase 8 (retro) — the cycle is NOT complete until retro has run
3) Comment the PR link on the originating issue
4) If GitHub backend: update issue state label to "complete"
EOF
