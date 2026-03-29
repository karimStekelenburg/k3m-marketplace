---
name: component-development
description: >-
  This skill should be used when the user asks to "create a slash command",
  "add a command", "create a hook", "add a PreToolUse/PostToolUse hook",
  "create an agent", "write a subagent", "add MCP server", "integrate MCP",
  "configure MCP in plugin", "use .mcp.json", or needs guidance on any
  plugin component: commands, hooks, agents, MCP servers, or output styles.
version: 0.3.0
---

# Component Development

Create and configure Claude Code plugin components — commands, hooks, agents, MCP servers, and output styles.

## Grounding Rule (MANDATORY)

Before answering ANY question about Claude Code component capabilities, syntax, or configuration:

1. **Discover doc pages**: Run `firecrawl map https://code.claude.com/docs/en/` to see all available pages (optionally add `--search "<component-type>"` to narrow)
2. **Fetch the content**: Run `firecrawl scrape <url> -f markdown -o .firecrawl/<topic>.md` to get the full page
3. **Read the fetched content**: Use Read tool on the output file, then answer based on what the docs actually say
4. **Never** answer from memory alone when the question involves what Claude Code supports
5. **Never** hardcode doc URLs — always discover them fresh

Key doc pages to search for: `commands`, `hooks`, `agents`, `mcp`, `output-styles`, `plugins-reference`

## Component Quick Reference

### Commands (`commands/*.md`)

Slash commands are markdown files with optional YAML frontmatter. They are instructions FOR Claude, not programs.

Key frontmatter fields: `description`, `allowed-tools`, `model`, `effort`, `argument-hint`, `disable-model-invocation`

Features:
- `$ARGUMENTS` and positional args (`$1`, `$2`) for dynamic input
- `@path/to/file` syntax to include file contents
- `` !`command` `` for inline bash execution
- Subdirectories create namespaced commands

### Hooks (`hooks/hooks.json`)

Event-driven automation. Plugin format wraps with `{"hooks": {EVENT: [...]}}`.

Hook types: `command`, `prompt`, `agent`, `http`

Key events: PreToolUse, PostToolUse, Stop, SessionStart, SessionEnd, PreCompact, PostCompact, UserPromptSubmit, Notification, SubagentStop

Important:
- Use `${CLAUDE_PLUGIN_ROOT}` in hook commands for portability
- Prompt-based hooks recommended for complex logic
- Hooks load at session start — require restart for changes
- `$CLAUDE_ENV_FILE` in SessionStart hooks to persist env vars
- PreToolUse can return `permissionDecision: allow|deny|ask`

### Agents (`agents/*.md`)

Subagent definitions with YAML frontmatter and system prompt body.

Required frontmatter: `name`, `description`, `model`, `color`
Optional: `effort`, `maxTurns`, `disallowedTools`, `tools`, `initialPrompt`, `hooks`

Key patterns:
- Description uses third-person with `<example>` blocks for triggering
- System prompt uses second person ("You are...")
- `hooks` field allows inline hook definitions scoped to agent lifetime
- `initialPrompt` auto-submits first turn

### MCP Servers (`.mcp.json`)

External tool integration via Model Context Protocol.

Server types: `stdio` (local process), `http` (streamable HTTP — recommended for remote)

Key patterns:
- `${CLAUDE_PLUGIN_ROOT}` in server commands for portability
- Tool naming: `mcp__plugin_<plugin>_<server>__<tool>`
- OAuth handled automatically for http servers
- Test with `/mcp` command to verify servers loaded

### Output Styles (`output-styles/*.md`)

Response behavior modification via markdown files + SessionStart hook injection.

**Always fetch current docs for the latest output styles specification.**

## Marketplace-Specific Rules

- Components are auto-discovered from standard directories
- Use `${CLAUDE_PLUGIN_ROOT}` for all internal path references
- Natural language files are code — check dependencies before removing (see `docs/file-roles-and-dependencies.md`)
- Agent `<example>` blocks need `description: |` block scalar for YAML validation
