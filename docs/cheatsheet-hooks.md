# hooks.json — Complete Schema Reference

Location: `<plugin-root>/hooks/hooks.json`

Hooks are event-driven automation scripts that execute in response to Claude Code events.

## File Format

Plugin hooks use a wrapper format:

```json
{
  "description": "Optional description of these hooks",
  "hooks": {
    "<EventName>": [
      {
        "matcher": "<pattern>",
        "hooks": [
          {
            "type": "command|prompt",
            "command": "...",
            "prompt": "...",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

**Important:** The `"hooks"` wrapper is required for plugin hooks.json. Settings-format hooks (in `.claude/settings.json`) use events directly at top level without the wrapper.

## Hook Events

| Event | When | Supports prompt type |
|-------|------|---------------------|
| `PreToolUse` | Before any tool runs | Yes |
| `PostToolUse` | After tool completes | Yes |
| `Stop` | Main agent considers stopping | Yes |
| `SubagentStop` | Subagent considers stopping | Yes |
| `UserPromptSubmit` | User submits a prompt | Yes |
| `SessionStart` | Session begins | No (command only) |
| `SessionEnd` | Session ends | No (command only) |
| `PreCompact` | Before context compaction | No (command only) |
| `Notification` | Claude sends notification | No (command only) |

## Hook Types

### command
Execute a shell command:
```json
{
  "type": "command",
  "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/validate.py",
  "timeout": 60
}
```
- **Default timeout:** 60 seconds
- Receives JSON via stdin
- Use for fast, deterministic checks

### prompt
LLM-driven decision making:
```json
{
  "type": "prompt",
  "prompt": "Evaluate if this tool use is safe: $TOOL_INPUT",
  "timeout": 30
}
```
- **Default timeout:** 30 seconds
- Only supported on: PreToolUse, PostToolUse, Stop, SubagentStop, UserPromptSubmit
- Use for context-aware, complex reasoning

## Matchers

### Exact match
```json
"matcher": "Write"
```

### Multiple tools (pipe-separated)
```json
"matcher": "Read|Write|Edit"
```

### Wildcard
```json
"matcher": "*"
```

### Regex
```json
"matcher": "mcp__.*__delete.*"
```

**Note:** Matchers are case-sensitive. Omitting matcher is equivalent to `"*"`.

## Hook Input (stdin JSON)

All hooks receive:
```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.txt",
  "cwd": "/current/working/dir",
  "permission_mode": "ask|allow",
  "hook_event_name": "PreToolUse"
}
```

Event-specific fields:
- **PreToolUse/PostToolUse:** `tool_name`, `tool_input`, `tool_result` (PostToolUse only)
- **UserPromptSubmit:** `user_prompt`
- **Stop/SubagentStop:** `reason`

Prompt hooks can reference: `$TOOL_INPUT`, `$TOOL_RESULT`, `$USER_PROMPT`

## Hook Output

### Standard output (all hooks)
```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Message for Claude"
}
```

### PreToolUse-specific output
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask",
    "updatedInput": {"field": "modified_value"}
  },
  "systemMessage": "Explanation for Claude"
}
```

### Stop/SubagentStop-specific output
```json
{
  "decision": "approve|block",
  "reason": "Explanation",
  "systemMessage": "Additional context"
}
```

## Exit Codes

- `0` — Success (stdout shown in transcript)
- `2` — Blocking error (stderr fed back to Claude)
- Other — Non-blocking error

## Environment Variables

Available in command hooks:
- `$CLAUDE_PROJECT_DIR` — Project root path
- `$CLAUDE_PLUGIN_ROOT` — Plugin directory (use for portable paths)
- `$CLAUDE_PLUGIN_DATA` — Persistent data directory (`~/.claude/plugins/data/{id}/`)
- `$CLAUDE_ENV_FILE` — SessionStart only: append env vars here to persist them
- `$CLAUDE_CODE_REMOTE` — Set if running in remote context

## Execution Model

- All matching hooks run **in parallel**
- Hooks don't see each other's output
- Non-deterministic ordering
- Plugin hooks merge with user hooks

## Gotchas

1. **Hooks load at session start** — changes require restarting Claude Code
2. **Use `${CLAUDE_PLUGIN_ROOT}`** in all command paths for portability
3. **Plugin format requires `"hooks"` wrapper** — settings format does not
4. **Multiple hooks in one entry run in parallel** — design for independence
5. **Prompt hooks only on subset of events** — not available for SessionStart/End
6. **SessionStart can persist env vars** via `$CLAUDE_ENV_FILE`
7. **Always quote bash variables** — `"$file_path"` not `$file_path`

## Complete Example

```json
{
  "description": "Security and quality validation hooks",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/validate-write.py",
            "timeout": 10
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if this bash command is safe: $TOOL_INPUT"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/post-edit.sh",
            "timeout": 30
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Verify task is complete: tests run, build passes, questions answered."
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/load-context.sh"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/prompt-filter.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```
