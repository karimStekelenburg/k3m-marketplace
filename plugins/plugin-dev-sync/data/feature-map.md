# Claude Code Feature Map

Generated: 2026-03-28
Sources analyzed: 15
Latest version observed: v2.1.85

---

## Plugin System

### plugin.json Schema Fields

| Field | Type | Required | Default | Description | Source(s) | Confidence |
|-------|------|----------|---------|-------------|-----------|------------|
| `name` | string | **yes** | — | Unique identifier, kebab-case, 3-50 chars | [docs](https://docs.anthropic.com/en/docs/claude-code/plugins), [gh](https://github.com/anthropics/claude-code) | high |
| `version` | string (semver) | no | — | Semantic versioning | docs | medium |
| `description` | string | no | — | Shown in plugin manager | docs | high |
| `author` | object | no | — | `{name, email, url}` | docs | high |
| `homepage` | string (URL) | no | — | Plugin homepage | docs | medium |
| `repository` | string (URL) | no | — | Source repository | docs | medium |
| `license` | string | no | — | License identifier | docs | medium |
| `keywords` | string[] | no | — | Search keywords | docs | medium |
| `commands` | string \| string[] | no | `"./commands"` | Auto-discovered; custom paths supplement | docs | high |
| `agents` | string \| string[] | no | `"./agents"` | Auto-discovered; custom paths supplement | docs | high |
| `skills` | string \| string[] | no | `"./skills"` | Auto-discovered; custom paths supplement | docs | high |
| `hooks` | string | no | `"./hooks/hooks.json"` | Path to hooks config | docs | high |
| `mcpServers` | string \| object | no | `./.mcp.json` | MCP server definitions (path or inline) | docs, mcp-docs | high |
| `lspServers` | object | no | — | LSP server definitions (inline only) | docs | high |
| `outputStyles` | string \| string[] | no | `"./output-styles"` | Output style definitions | docs | medium |

### Plugin Directory Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Manifest (ONLY file in .claude-plugin/)
├── commands/                 # Slash commands (.md files)
├── agents/                   # Subagent definitions (.md files)
├── skills/                   # Skills (subdirs with SKILL.md)
├── hooks/
│   └── hooks.json           # Hook configuration
├── .mcp.json                # MCP server config
├── .lsp.json                # LSP server config
├── settings.json            # Default settings (only `agent` key supported)
└── output-styles/           # Output style definitions
```

### Plugin Variables

| Variable | Description | Source(s) | Confidence |
|----------|-------------|-----------|------------|
| `${CLAUDE_PLUGIN_ROOT}` | Resolves to the plugin's root directory at runtime | docs, gh releases (v2.1.78) | high |
| `${CLAUDE_PLUGIN_DATA}` | Persistent plugin state that survives updates; `/plugin uninstall` prompts before deleting | gh releases (v2.1.78) | high |
| `CLAUDE_CODE_PLUGIN_SEED_DIR` | Env var to seed plugin directories; supports multiple dirs separated by platform path delimiter | gh releases (v2.1.79) | high |

### Plugin Management

- `claude plugin install <name>` / `claude plugin validate` / `claude plugin enable` / `claude plugin disable`
- `--plugin-dir ./path` loads a plugin for the session only; can repeat for multiple
- `/reload-plugins` reloads all plugins mid-session without restart
- Local `--plugin-dir` overrides installed marketplace plugin of same name (except managed)
- Version >= 1.0.33 required for plugin support

### Marketplace

- `marketplace.json` at `.claude-plugin/marketplace.json`
- `strict: true` (default): plugin.json is authority, marketplace supplements
- `strict: false`: marketplace entry is the entire definition
- `source: 'settings'` marketplace type: declare plugin entries inline in settings.json (v2.1.80)
- Submission: claude.ai/settings/plugins/submit or platform.claude.com/plugins/submit

---

## Skills (SKILL.md)

### Frontmatter Fields

| Field | Type | Required | Default | Description | Source(s) | Confidence |
|-------|------|----------|---------|-------------|-----------|------------|
| `name` | string | yes | — | Kebab-case identifier | docs | high |
| `description` | string | yes | — | Trigger mechanism: tells Claude WHEN to invoke | docs | high |
| `version` | string (semver) | no | — | Skill version | docs | medium |
| `license` | string | no | — | License identifier | docs | medium |
| `allowed-tools` | string (comma-sep) | no | — | Pre-allow specific tools | docs | high |
| `argument-hint` | string | no | — | Hint for autocomplete | docs | medium |
| `model` | string | no | inherit | `sonnet`, `opus`, `haiku` | docs | high |
| `effort` | string | no | — | Override effort level when skill is invoked | gh releases (v2.1.80) | high |
| `disable-model-invocation` | boolean | no | `false` | Prevent auto-invocation | docs | high |
| `user-invocable` | boolean | no | `true` | Set false to hide from slash menu | docs | medium |

### Skill Structure

```
skills/
└── my-skill/
    ├── SKILL.md              # Required
    ├── references/           # Optional reference materials
    ├── examples/             # Optional examples
    └── scripts/              # Optional helper scripts
```

### Key Behaviors

- Skills are namespaced by plugin: `/plugin-name:skill-name`
- `$ARGUMENTS` placeholder captures user input after the skill name
- Descriptions in `/skills` listing capped at 250 chars (v2.1.83)
- `/skills` menu sorted alphabetically (v2.1.83)

---

## Agents (Subagents)

### Frontmatter Fields

| Field | Type | Required | Default | Description | Source(s) | Confidence |
|-------|------|----------|---------|-------------|-----------|------------|
| `name` | string | yes | — | Lowercase, numbers, hyphens; 3-50 chars | docs | high |
| `description` | string | yes | — | Must include `<example>` blocks for triggering | docs | high |
| `model` | string | yes | — | `inherit`, `sonnet`, `opus`, `haiku` | docs | high |
| `color` | string | yes | — | `blue`, `cyan`, `green`, `yellow`, `magenta`, `red` | docs | high |
| `tools` | string[] | no | all tools | Restrict to specific tools | docs | high |
| `effort` | string | no | — | Override effort level | gh releases (v2.1.78) | high |
| `maxTurns` | number | no | — | Limit agentic turns | gh releases (v2.1.78) | high |
| `disallowedTools` | string[] | no | — | Tools to exclude | gh releases (v2.1.78) | high |

### Agent Locations

- User: `~/.claude/agents/` (all projects)
- Project: `.claude/agents/` (shared via git)
- Plugin: `<plugin>/agents/`

### Key Behaviors

- Agent auto-namespaced by plugin
- `settings.json` `agent` key activates a subagent as the main thread
- Dynamic agents via CLI: `--agents '{"name":{"description":"...","prompt":"..."}}'`
- `--agent my-custom-agent` overrides the agent setting for a session

---

## Hook Events

| Event | When | Matcher Target | Decision Control | Source(s) | Confidence |
|-------|------|----------------|------------------|-----------|------------|
| `SessionStart` | Session begins/resumes | `startup`, `resume`, `clear`, `compact` | Persist env vars | docs | high |
| `SessionEnd` | Session terminates | `clear`, `resume`, `logout`, `prompt_input_exit`, etc. | — | docs | high |
| `UserPromptSubmit` | Prompt submitted, before processing | no matcher | Can block/modify | docs | high |
| `InstructionsLoaded` | CLAUDE.md or rules file loaded | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` | — | docs | high |
| `PreToolUse` | Before tool executes | tool name (e.g. `Bash`, `Edit\|Write`, `mcp__*`) | `allow`, `deny`, `block` | docs | high |
| `PostToolUse` | After tool succeeds | tool name | — | docs | high |
| `PostToolUseFailure` | After tool fails | tool name | — | docs | high |
| `PermissionRequest` | Permission dialog appears | tool name | — | docs | high |
| `Notification` | CC sends notification | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog` | — | docs | high |
| `SubagentStart` | Subagent spawned | agent type/name | — | docs | high |
| `SubagentStop` | Subagent finishes | agent type/name | — | docs | high |
| `TaskCreated` | Task created via TaskCreate | no matcher | — | gh (v2.1.84) | high |
| `TaskCompleted` | Task marked completed | no matcher | — | docs | high |
| `Stop` | Claude finishes responding | no matcher | Can block | docs | high |
| `StopFailure` | Turn ends due to API error | `rate_limit`, `authentication_failed`, `billing_error`, `invalid_request`, `server_error`, `max_output_tokens`, `unknown` | ignored | gh (v2.1.78) | high |
| `TeammateIdle` | Teammate about to go idle | no matcher | — | docs | high |
| `ConfigChange` | Config file changes | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` | — | docs | high |
| `CwdChanged` | Working directory changes | no matcher (always fires) | — | docs | high |
| `FileChanged` | Watched file changes on disk | filename (basename) | — | docs | high |
| `WorktreeCreate` | Worktree being created | no matcher | Replaces default git behavior | docs, gh (v2.1.84) | high |
| `WorktreeRemove` | Worktree being removed | no matcher | — | docs | high |
| `PreCompact` | Before compaction | `manual`, `auto` | — | docs | high |
| `PostCompact` | After compaction | `manual`, `auto` | — | docs | high |
| `Elicitation` | MCP server requests user input | MCP server name | — | docs | high |
| `ElicitationResult` | User responds to elicitation | MCP server name | — | docs | high |

### Hook Handler Types

| Type | Description | Key Fields |
|------|-------------|------------|
| `command` | Shell command; receives JSON on stdin | `command`, `async`, `shell` (`bash`/`powershell`) |
| `http` | POST to URL with JSON body | `url`, `headers`, `allowedEnvVars` |
| `prompt` | Single-turn LLM evaluation; returns yes/no JSON | — |
| `agent` | Spawns subagent with tools (Read, Grep, Glob) | — |

### Common Handler Fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | yes | `"command"`, `"http"`, `"prompt"`, or `"agent"` |
| `if` | no | Permission rule syntax filter (e.g. `"Bash(git *)"`) — tool events only. Added v2.1.85 |
| `timeout` | no | Seconds. Defaults: 600 (command), 30 (prompt), 60 (agent) |
| `statusMessage` | no | Custom spinner message |
| `once` | no | If true, runs once per session (skills only) |

### Hook Locations

| Location | Scope |
|----------|-------|
| `~/.claude/settings.json` | All projects (user) |
| `.claude/settings.json` | Single project (shared) |
| `.claude/settings.local.json` | Single project (local) |
| Managed policy settings | Organization-wide |
| Plugin `hooks/hooks.json` | When plugin enabled |
| Skill/agent frontmatter | While component active |

---

## MCP Configuration

### .mcp.json Schema

```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",            // "stdio", "sse", or "http"
      "command": "npx",
      "args": ["server"],
      "env": { "KEY": "value" },
      "oauth": {
        "authServerMetadataUrl": "..."
      }
    }
  }
}
```

### Transport Types

| Transport | Description |
|-----------|-------------|
| `stdio` | Local process; ideal for system access |
| `sse` | Server-Sent Events over HTTP |
| `http` | HTTP Streamable transport |

### Scopes

| Scope | Location |
|-------|----------|
| User/local | `~/.claude.json` (`mcpServers` field) |
| Project | `.mcp.json` in project root (committed) |
| Plugin | `.mcp.json` at plugin root or inline in `plugin.json` |
| Managed | `managed-mcp.json` in system dirs |

### Key Features

- Env var expansion in `.mcp.json` files
- `claude mcp add --transport <type> <name> <command/url>`
- `claude mcp reset-project-choices` to reset approval
- MCP tools follow pattern `mcp__<server>__<tool>`
- Elicitation: servers can request structured user input mid-task
- MCP OAuth: supports RFC 9728, Client ID Metadata Document (CIMD/SEP-991), Dynamic Client Registration (v2.1.81)
- `CLAUDE_CODE_MCP_SERVER_NAME` and `CLAUDE_CODE_MCP_SERVER_URL` env vars for headersHelper scripts (v2.1.85)
- Plugin MCP servers duplicating org-managed connectors are suppressed (v2.1.82)

---

## LSP Configuration

### .lsp.json Schema

```json
{
  "language-id": {
    "command": "language-server-binary",
    "args": ["serve"],
    "extensionToLanguage": {
      ".ext": "language-id"
    }
  }
}
```

- Users must have the language server binary installed
- Pre-built LSP plugins available for TypeScript, Python, Rust on official marketplace
- Can also be defined inline in `plugin.json` under `lspServers`

---

## Commands (Slash Commands)

### Frontmatter Fields

| Field | Type | Description | Confidence |
|-------|------|-------------|------------|
| `description` | string | Shown in command menu | high |
| `allowed-tools` | string | Pre-allow tools | high |
| `argument-hint` | string | Autocomplete hint | high |
| `disable-model-invocation` | boolean | Prevent auto-invocation | high |
| `effort` | string | Override effort level (v2.1.80) | high |

- Commands live in `commands/` directory as `.md` files
- Plugin commands namespaced as `/plugin-name:command-name`

---

## Settings (settings.json)

### Key Settings

| Setting | Type | Description | Confidence |
|---------|------|-------------|------------|
| `permissions.allow` | string[] | Permission rules to allow | high |
| `permissions.deny` | string[] | Permission rules to deny | high |
| `permissions.ask` | string[] | Permission rules requiring confirmation | high |
| `permissions.defaultMode` | string | Default permission mode | high |
| `permissions.additionalDirectories` | string[] | Extra working directories | high |
| `permissions.disableBypassPermissionsMode` | string | `"disable"` to block bypass mode | high |
| `model` | string | Override default model | high |
| `availableModels` | string[] | Restrict model selection | high |
| `modelOverrides` | object | Map model IDs to provider-specific IDs | high |
| `effortLevel` | string | Persist effort (`low`/`medium`/`high`) | high |
| `env` | object | Environment variables for every session | high |
| `hooks` | object | Hook configuration | high |
| `agent` | string | Run main thread as named subagent | high |
| `outputStyle` | string | Active output style | high |
| `autoMode` | object | Auto mode classifier config (`environment`, `allow`, `soft_deny`) | high |
| `disableAutoMode` | string | `"disable"` to prevent auto mode | high |
| `autoMemoryDirectory` | string | Custom auto memory directory | high |
| `cleanupPeriodDays` | number | Session cleanup period (default: 30) | high |
| `companyAnnouncements` | string[] | Startup announcements | high |
| `attribution` | object | Git commit/PR attribution config | high |
| `includeGitInstructions` | boolean | Include built-in git instructions (default: true) | high |
| `statusLine` | object | Custom status line config | high |
| `fileSuggestion` | object | Custom @ file autocomplete | high |
| `respectGitignore` | boolean | Whether @ picker respects .gitignore (default: true) | high |
| `apiKeyHelper` | string | Script to generate auth value | high |
| `language` | string | Preferred response language | high |
| `voiceEnabled` | boolean | Push-to-talk voice dictation | high |
| `autoUpdatesChannel` | string | `"stable"` or `"latest"` | high |
| `spinnerVerbs` | object | Custom spinner verbs | medium |
| `spinnerTipsEnabled` | boolean | Show tips in spinner (default: true) | medium |
| `spinnerTipsOverride` | object | Custom spinner tips | medium |
| `prefersReducedMotion` | boolean | Reduce UI animations | medium |
| `fastModePerSessionOptIn` | boolean | Require per-session fast mode opt-in | medium |
| `feedbackSurveyRate` | number | Survey probability (0-1) | medium |
| `plansDirectory` | string | Custom plans directory | medium |
| `showClearContextOnPlanAccept` | boolean | Show clear context option (default: false) | medium |
| `defaultShell` | string | `"bash"` or `"powershell"` | high |
| `forceLoginMethod` | string | `"claudeai"` or `"console"` | high |
| `forceLoginOrgUUID` | string | Auto-select org during login | medium |
| `enableAllProjectMcpServers` | boolean | Auto-approve project MCP servers | high |
| `enabledMcpjsonServers` | string[] | Specific MCP servers to approve | high |
| `disabledMcpjsonServers` | string[] | Specific MCP servers to reject | high |
| `alwaysThinkingEnabled` | boolean | Extended thinking by default | high |
| `disableAllHooks` | boolean | Disable all hooks and custom status line | high |
| `disableDeepLinkRegistration` | string | `"disable"` to prevent protocol handler | medium |

### Managed-Only Settings

| Setting | Description | Confidence |
|---------|-------------|------------|
| `allowManagedHooksOnly` | Block user/project/plugin hooks | high |
| `allowManagedPermissionRulesOnly` | Only managed permission rules apply | high |
| `allowManagedMcpServersOnly` | Only managed MCP allowlist applies | high |
| `allowedHttpHookUrls` | URL allowlist for HTTP hooks | high |
| `httpHookAllowedEnvVars` | Env var allowlist for HTTP hook headers | high |
| `strictKnownMarketplaces` | Marketplace allowlist | high |
| `blockedMarketplaces` | Marketplace blocklist | high |
| `pluginTrustMessage` | Custom message for plugin trust warning | medium |
| `channelsEnabled` | Allow channels for Team/Enterprise | high |
| `allowedChannelPlugins` | Channel plugin allowlist | high |
| `allowedMcpServers` | MCP server allowlist | high |
| `deniedMcpServers` | MCP server denylist | high |

### Global Config (~/.claude.json, not settings.json)

| Setting | Description | Default | Confidence |
|---------|-------------|---------|------------|
| `autoConnectIde` | Auto-connect to running IDE | false | high |
| `autoInstallIdeExtension` | Auto-install IDE extension | true | high |
| `editorMode` | `"normal"` or `"vim"` | `"normal"` | high |
| `showTurnDuration` | Show turn duration messages | true | high |
| `terminalProgressBarEnabled` | Terminal progress bar | true | high |
| `teammateMode` | `"auto"`, `"in-process"`, `"tmux"` | `"auto"` | high |

### Worktree Settings

| Setting | Description | Confidence |
|---------|-------------|------------|
| `worktree.symlinkDirectories` | Directories to symlink from main repo | high |
| `worktree.sparsePaths` | Sparse checkout paths (cone mode) | high |

### Settings Precedence (high to low)

1. Managed (server-managed > MDM/OS > file-based)
2. Command-line arguments
3. Local (`.claude/settings.local.json`)
4. Project (`.claude/settings.json`)
5. User (`~/.claude/settings.json`)

---

## CLI Flags & Options

| Flag | Description | Source(s) | Confidence |
|------|-------------|-----------|------------|
| `--add-dir` | Additional working directories | docs | high |
| `--agent` | Specify agent for session | docs | high |
| `--agents` | Define subagents dynamically via JSON | docs | high |
| `--allowedTools` | Tools that execute without permission | docs | high |
| `--append-system-prompt` | Append to default system prompt | docs | high |
| `--append-system-prompt-file` | Append file contents to system prompt | docs | high |
| `--bare` | Minimal mode: skip hooks, LSP, plugins, skills, memory, CLAUDE.md | docs, gh (v2.1.81) | high |
| `--betas` | Beta headers for API requests | docs | medium |
| `--channels` | MCP channel notifications (research preview) | docs, gh (v2.1.80) | high |
| `--chrome` / `--no-chrome` | Enable/disable Chrome integration | docs | high |
| `--continue`, `-c` | Resume most recent conversation | docs | high |
| `--dangerously-skip-permissions` | Skip permission prompts | docs | high |
| `--debug` | Debug mode with category filtering | docs | high |
| `--disable-slash-commands` | Disable all skills/commands | docs | high |
| `--disallowedTools` | Remove tools from model context | docs | high |
| `--effort` | Set effort level (`low`, `medium`, `high`, `max` for Opus 4.6) | docs | high |
| `--enable-auto-mode` | Unlock auto mode in Shift+Tab cycle | docs | high |
| `--fallback-model` | Fallback model when default overloaded (print only) | docs | high |
| `--fork-session` | New session ID when resuming | docs | high |
| `--from-pr` | Resume sessions linked to a GitHub PR | docs | high |
| `--ide` | Auto-connect to IDE | docs | high |
| `--init` / `--init-only` | Run initialization hooks | docs | high |
| `--input-format` | Input format for print mode (`text`, `stream-json`) | docs | high |
| `--json-schema` | Validated JSON output matching schema (print mode) | docs | high |
| `--maintenance` | Run maintenance hooks and exit | docs | high |
| `--max-budget-usd` | Maximum API spend (print mode) | docs | high |
| `--max-turns` | Limit agentic turns (print mode) | docs | high |
| `--mcp-config` | Load MCP servers from JSON | docs | high |
| `--model` | Set model for session (alias: `sonnet`, `opus`) | docs | high |
| `--name`, `-n` | Session display name | docs | high |
| `--no-session-persistence` | Disable session persistence (print mode) | docs | high |
| `--output-format` | Output format (`text`, `json`, `stream-json`) | docs | high |
| `--permission-mode` | Begin in specified permission mode | docs | high |
| `--permission-prompt-tool` | MCP tool for permission prompts | docs | high |
| `--plugin-dir` | Load plugin from directory | docs | high |
| `--print`, `-p` | Print mode (non-interactive) | docs | high |
| `--remote` | Create web session on claude.ai | docs | high |
| `--remote-control`, `--rc` | Start with Remote Control enabled | docs | high |
| `--resume`, `-r` | Resume session by ID or name | docs | high |
| `--session-id` | Use specific UUID for conversation | docs | high |
| `--setting-sources` | Comma-separated setting sources to load | docs | high |
| `--settings` | Additional settings JSON file or string | docs | high |
| `--strict-mcp-config` | Only use MCP from --mcp-config | docs | high |
| `--system-prompt` | Replace entire system prompt | docs | high |
| `--system-prompt-file` | Replace system prompt from file | docs | high |
| `--teammate-mode` | `auto`, `in-process`, `tmux` | docs | high |
| `--teleport` | Resume web session locally | docs | high |
| `--tools` | Restrict built-in tools | docs | high |
| `--verbose` | Verbose logging | docs | high |
| `--version`, `-v` | Print version | docs | high |
| `--worktree`, `-w` | Start in isolated git worktree | docs | high |
| `--tmux` | Create tmux session for worktree | docs | high |
| `--console` (auth login) | Sign in with Anthropic Console (API billing) | gh (v2.1.79) | high |
| `--include-partial-messages` | Partial streaming events (print+stream-json) | docs | medium |
| `--dangerously-load-development-channels` | Load unapproved channels | docs | medium |

### Core Subcommands

| Command | Description |
|---------|-------------|
| `claude` | Start interactive session |
| `claude "query"` | Interactive with initial prompt |
| `claude -p "query"` | Print mode (SDK) |
| `claude -c` | Continue most recent conversation |
| `claude -r <id>` | Resume by ID or name |
| `claude update` | Update to latest |
| `claude auth login/logout/status` | Authentication |
| `claude agents` | List configured subagents |
| `claude auto-mode defaults` | Print auto mode classifier rules |
| `claude mcp ...` | MCP server management |
| `claude plugin ...` | Plugin management |
| `claude remote-control` | Start Remote Control server |

---

## Memory System

### CLAUDE.md Files

| Location | Scope | Shared |
|----------|-------|--------|
| `~/.claude/CLAUDE.md` | All projects (user) | No |
| `CLAUDE.md` or `.claude/CLAUDE.md` | Project root | Yes |
| `.claude/rules/*.md` | Project rules | Yes |

- Delivered as user message after system prompt (not part of system prompt)
- Survives `/compact` (re-read from disk)
- Supports `@path` imports for additional files
- `--append-system-prompt` for system-prompt-level instructions

### Auto Memory

- Location: `~/.claude/projects/<project>/memory/`
- `MEMORY.md` entrypoint: first 200 lines or 25KB loaded at session start
- Topic files loaded on demand
- Machine-local; shared across worktrees within same git repo
- Enable/disable: `autoMemoryEnabled` in settings or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`
- Custom location: `autoMemoryDirectory` setting (not accepted in project settings)
- `/memory` command to browse and edit

---

## Output Styles

- Configured via `outputStyle` setting or `/output-style` command
- Official plugins: `explanatory-output-style`, `learning-output-style` on gh
- Output style files live in `output-styles/` directory with `.md` extension
- Plugin field: `outputStyles` in plugin.json

---

## Models

| Model | Notes | Source | Confidence |
|-------|-------|--------|------------|
| `claude-sonnet-4-6` | Alias: `sonnet` | docs | high |
| `claude-opus-4-6` | Alias: `opus`. Supports `--effort max` | docs | high |
| `claude-haiku-3-5` | Alias: `haiku` | docs | medium |

- `/model` to switch mid-session
- `availableModels` setting restricts selection
- `modelOverrides` maps to provider-specific IDs (Bedrock ARNs, etc.)
- `ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU}_MODEL_SUPPORTS` env vars for capability detection (v2.1.84)
- Providers: Anthropic API, Amazon Bedrock, Google Vertex AI, Microsoft Foundry

---

## Recent Release Highlights (v2.1.78-v2.1.85)

| Version | Key Features | Confidence |
|---------|-------------|------------|
| v2.1.85 | Conditional `if` field for hooks; `CLAUDE_CODE_MCP_SERVER_NAME/URL` env vars; PreToolUse can satisfy AskUserQuestion; managed plugins hidden from marketplace | high |
| v2.1.84 | PowerShell tool (opt-in preview); TaskCreated hook; WorktreeCreate HTTP hooks; `ANTHROPIC_DEFAULT_*_MODEL_SUPPORTS` env vars | high |
| v2.1.83 | Skill description cap 250 chars; `/skills` sorted alphabetically; Read tool compact format | high |
| v2.1.82 | `--bare` flag; `--channels` permission relay; plugin MCP dedup with org connectors; Deprecated TaskOutput tool | high |
| v2.1.81 | `--bare` flag (scripted -p); `--channels` permission relay; MCP OAuth CIMD/SEP-991 | high |
| v2.1.80 | `source: 'settings'` marketplace; `effort` frontmatter for skills/commands; `--channels` research preview; `rate_limits` in statusline | high |
| v2.1.79 | `--console` auth login; `CLAUDE_CODE_PLUGIN_SEED_DIR` multiple dirs; VSCode `/remote-control` | high |
| v2.1.78 | StopFailure hook; `${CLAUDE_PLUGIN_DATA}` variable; `effort`/`maxTurns`/`disallowedTools` agent frontmatter; line-by-line streaming | high |

---

## Contradictions Found

- None detected between official docs and GitHub releases. The sources are consistent.

## Low-Confidence Discoveries

- Twitter sources (alexalbert, anthropic, karpathy, amanrsanger) could not be parsed for structured feature data due to HTML/JS rendering. No features were extracted exclusively from social sources.

## Notes on Source Quality

- The cached files are raw HTML dumps, heavily padded with CSS/JS framework code. Actual documentation content is a small fraction of file size.
- The `docs-claude-code.txt` file is a sitemap root containing navigation JSON from all language versions, not page content. Subagent docs, skills docs, and other child pages are not individually cached.
- **Recommendation**: Add these URLs to `resources.json` for better coverage:
  - `https://docs.anthropic.com/en/docs/claude-code/sub-agents` (subagent frontmatter reference)
  - `https://docs.anthropic.com/en/docs/claude-code/skills` (skill authoring guide)
  - `https://docs.anthropic.com/en/docs/claude-code/output-styles` (output style reference)
  - `https://docs.anthropic.com/en/docs/claude-code/permissions` (permission rule syntax)
  - `https://docs.anthropic.com/en/docs/claude-code/plugins-reference` (full plugin reference)
  - `https://docs.anthropic.com/en/docs/claude-code/channels` (channels reference)
  - `https://docs.anthropic.com/en/docs/claude-code/env-vars` (environment variables reference)
  - `https://docs.anthropic.com/en/docs/claude-code/tools-reference` (tools reference)
