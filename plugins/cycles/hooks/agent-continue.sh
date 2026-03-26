#!/usr/bin/env bash
# PostToolUse hook for Agent completions.
# When a cycle subagent finishes, force continuation to the next phase.
set -euo pipefail

AGENT_TYPE=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.subagent_type // empty')

if echo "$AGENT_TYPE" | grep -qiE 'code-reviewer|test-writer|verification-gate|ui-verifier'; then
  echo "GUARDRAIL: Subagent $AGENT_TYPE completed. Check result and continue to the NEXT phase. Do NOT stop or ask the user." >&2
fi
