#!/usr/bin/env bash
# PreToolUse hook for Skill invocations.
# When /cycle is invoked, remind Claude to execute all phases inline.
set -euo pipefail

SKILL_NAME=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.skill // empty')

if [[ "$SKILL_NAME" == "cycle" ]]; then
  cat >&2 <<'EOF'
NOTICE: /cycle invoked — all 9 phases (0-8) must execute without pausing.
Do NOT use the Skill tool to invoke sub-skills (/spec, /plan, /retro) — execute their logic inline.

Backend detection: Check $K3M_BACKEND or run detect-backend.sh.
- fs: Read/write docs/ directory
- github: Read/write via GitHub API (issues, comments, project board)

State machine: Every phase transition must be valid. Use state-machine.sh to validate.
EOF
fi
