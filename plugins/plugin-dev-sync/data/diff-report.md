# Diff Report: Feature Map vs plugin-dev

Generated: 2026-03-28
Feature map version: v2.1.85
Plugin-dev last updated: pre-v2.1.78 (with partial v2.1.80 patches)

---

## Changes

### [Missing `effort` frontmatter in agent-development skill]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/agent-development/SKILL.md`
- **Current state**: Frontmatter fields table lists `name`, `description`, `model`, `color`, `tools`, `initialPrompt`, `hooks` but omits `effort`
- **Proposed state**: Add `effort` (string, optional) -- override effort level for the agent. Values: `low`, `medium`, `high`. Added in v2.1.78.
- **Sources**: Feature map "Agents > Frontmatter Fields" (`effort` field, gh releases v2.1.78)
- **Reasoning**: The feature map documents `effort` as a supported agent frontmatter field since v2.1.78. Plugin-dev omits it entirely.

---

### [Missing `maxTurns` frontmatter in agent-development skill]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/agent-development/SKILL.md`
- **Current state**: Not covered
- **Proposed state**: Add `maxTurns` (number, optional) -- limit agentic turns. Added in v2.1.78.
- **Sources**: Feature map "Agents > Frontmatter Fields" (`maxTurns` field, gh releases v2.1.78)
- **Reasoning**: Documented in feature map but absent from plugin-dev agent reference.

---

### [Missing `disallowedTools` frontmatter in agent-development skill]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/agent-development/SKILL.md`
- **Current state**: Not covered
- **Proposed state**: Add `disallowedTools` (string[], optional) -- tools to exclude from the agent. Added in v2.1.78.
- **Sources**: Feature map "Agents > Frontmatter Fields" (`disallowedTools` field, gh releases v2.1.78)
- **Reasoning**: Complements existing `tools` field. Feature map lists it as high confidence.

---

### [WebSocket MCP transport does not exist]
- **Type**: deprecated
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/mcp-integration/SKILL.md`, `plugins/plugin-dev/skills/mcp-integration/references/server-types.md`
- **Current state**: MCP integration skill documents a `ws` (WebSocket) transport type with full configuration examples, and includes it in the quick reference table and server-types reference
- **Proposed state**: Remove WebSocket (`ws`) transport entirely. The feature map lists only three transport types: `stdio`, `sse`, and `http`. No WebSocket transport exists in Claude Code.
- **Sources**: Feature map "MCP Configuration > Transport Types" (only stdio, sse, http listed); docs, mcp-docs
- **Reasoning**: The WebSocket transport was fabricated in the original plugin-dev authoring. It appears nowhere in official documentation or release notes. The feature map explicitly lists only three transports.

---

### [SSE transport not marked as deprecated in SKILL.md]
- **Type**: outdated
- **Confidence**: medium
- **Target file(s)**: `plugins/plugin-dev/skills/mcp-integration/SKILL.md`
- **Current state**: SSE listed as a full peer transport type alongside stdio and HTTP with active recommendations to use it for cloud services
- **Proposed state**: The server-types reference already marks SSE as deprecated (good), but the main SKILL.md still actively recommends SSE. Add deprecation note to SKILL.md and recommend `http` for new remote integrations.
- **Sources**: Feature map "MCP Configuration > Transport Types" (lists SSE without deprecation note, but server-types.md already deprecates it based on prior sync work)
- **Reasoning**: The SKILL.md is the primary guidance surface. Its "Focus on stdio for custom/local servers, SSE for hosted services with OAuth" closing line actively steers users toward SSE.

---

### [Missing `outputStyles` plugin.json field]
- **Type**: missing
- **Confidence**: medium
- **Target file(s)**: `plugins/plugin-dev/skills/plugin-structure/SKILL.md`, `plugins/plugin-dev/skills/plugin-structure/references/manifest-reference.md`
- **Current state**: Neither the plugin structure skill nor the manifest reference mentions `outputStyles` as a plugin.json field
- **Proposed state**: Add `outputStyles` (string | string[], optional, default `"./output-styles"`) -- output style definitions directory. Also add `output-styles/` to the directory structure diagram.
- **Sources**: Feature map "plugin.json Schema Fields" (`outputStyles` field, docs)
- **Reasoning**: Output styles are a documented plugin.json feature. The plugin structure skill shows the directory layout but omits output-styles/.

---

### [Missing `settings.json` in plugin directory structure]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/plugin-structure/SKILL.md`
- **Current state**: Directory structure diagram does not include `settings.json`
- **Proposed state**: Add `settings.json` to the directory structure diagram with note: "Default settings (only `agent` key supported)"
- **Sources**: Feature map "Plugin Directory Structure" (shows `settings.json` with `agent` key)
- **Reasoning**: The feature map shows `settings.json` as part of the standard plugin directory structure. The `agent` key activates a subagent as the main thread.

---

### [Missing `${CLAUDE_PLUGIN_DATA}` variable documentation]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/plugin-structure/SKILL.md`, `plugins/plugin-dev/skills/hook-development/SKILL.md`
- **Current state**: Only `${CLAUDE_PLUGIN_ROOT}` is documented. `${CLAUDE_PLUGIN_DATA}` is not mentioned anywhere.
- **Proposed state**: Document `${CLAUDE_PLUGIN_DATA}` -- persistent plugin state directory that survives updates. `/plugin uninstall` prompts before deleting. Added v2.1.78.
- **Sources**: Feature map "Plugin Variables" (`${CLAUDE_PLUGIN_DATA}`, gh releases v2.1.78)
- **Reasoning**: This is a critical variable for plugins that need persistent state. High confidence from release notes.

---

### [Missing `CLAUDE_CODE_PLUGIN_SEED_DIR` documentation]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/plugin-structure/SKILL.md`
- **Current state**: Not covered
- **Proposed state**: Document `CLAUDE_CODE_PLUGIN_SEED_DIR` env var -- seeds plugin directories, supports multiple dirs separated by platform path delimiter. Added v2.1.79.
- **Sources**: Feature map "Plugin Variables" (`CLAUDE_CODE_PLUGIN_SEED_DIR`, gh releases v2.1.79)
- **Reasoning**: Useful for enterprise/team deployments that pre-seed plugins.

---

### [Missing hook events in hook-development skill]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/hook-development/SKILL.md`
- **Current state**: Quick reference table lists 9 events: PreToolUse, PostToolUse, UserPromptSubmit, Stop, SubagentStop, SessionStart, SessionEnd, PreCompact, Notification
- **Proposed state**: Add these missing events to the reference: `PostToolUseFailure`, `PermissionRequest`, `InstructionsLoaded`, `StopFailure`, `TaskCreated`, `TaskCompleted`, `TeammateIdle`, `ConfigChange`, `CwdChanged`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove`, `PostCompact`, `Elicitation`, `ElicitationResult`, `SubagentStart`
- **Sources**: Feature map "Hook Events" (full table with 24+ events from docs and gh releases)
- **Reasoning**: Plugin-dev documents fewer than half the available hook events. Many of the missing events (StopFailure, FileChanged, ConfigChange) are highly useful for plugin authors.

---

### [Missing `http` and `agent` hook handler types]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/hook-development/SKILL.md`
- **Current state**: Documents only `command` and `prompt` hook types
- **Proposed state**: Add `http` type (POST to URL with JSON body, fields: `url`, `headers`, `allowedEnvVars`) and `agent` type (spawns subagent with tools Read, Grep, Glob)
- **Sources**: Feature map "Hook Handler Types" (docs)
- **Reasoning**: Two of the four handler types are completely undocumented.

---

### [Missing `if` conditional field for hooks]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/hook-development/SKILL.md`
- **Current state**: Not covered
- **Proposed state**: Document `if` field (optional) -- permission rule syntax filter (e.g. `"Bash(git *)"`) for tool events only. Added v2.1.85.
- **Sources**: Feature map "Common Handler Fields" (`if` field, v2.1.85)
- **Reasoning**: This is a powerful new feature that allows conditional hook execution without wrapper scripts. High confidence from v2.1.85 release notes.

---

### [Missing `once` field for skill hooks]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/hook-development/SKILL.md`, `plugins/plugin-dev/skills/skill-development/SKILL.md`
- **Current state**: Not covered
- **Proposed state**: Document `once` field (boolean, optional) -- if true, hook runs only once per session. Skills-only feature.
- **Sources**: Feature map "Common Handler Fields" (`once` field, docs)
- **Reasoning**: Useful for one-time setup hooks in skills.

---

### [Hook timeout defaults are incorrect]
- **Type**: outdated
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/hook-development/SKILL.md`
- **Current state**: States "Defaults: Command hooks (60s), Prompt hooks (30s)"
- **Proposed state**: Should be: Command hooks (600s default), Prompt hooks (30s default), Agent hooks (60s default)
- **Sources**: Feature map "Common Handler Fields" (timeout defaults: 600 command, 30 prompt, 60 agent)
- **Reasoning**: The command hook default timeout is 600 seconds (10 minutes), not 60 seconds. This is a factual error that could cause confusion.

---

### [Missing `effort` frontmatter for skills]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/skill-development/SKILL.md`
- **Current state**: The "Additional Frontmatter Fields" section mentions `effort` briefly but the main SKILL.md frontmatter guide doesn't include it in the field table
- **Proposed state**: Ensure `effort` (string: `low`, `medium`, `high`) is documented as a standard skill frontmatter field. Added v2.1.80.
- **Sources**: Feature map "Skills > Frontmatter Fields" (`effort` field, gh releases v2.1.80)
- **Reasoning**: Already partially covered but needs to be in the primary field reference.

---

### [Missing skill description 250-char cap]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/skill-development/SKILL.md`
- **Current state**: Not mentioned
- **Proposed state**: Note that skill descriptions in the `/skills` listing are capped at 250 characters (v2.1.83), and `/skills` menu is sorted alphabetically.
- **Sources**: Feature map "Skills > Key Behaviors" (v2.1.83)
- **Reasoning**: Practical constraint that skill authors should know when writing descriptions.

---

### [Missing `user-invocable` skill frontmatter field]
- **Type**: missing
- **Confidence**: medium
- **Target file(s)**: `plugins/plugin-dev/skills/skill-development/SKILL.md`
- **Current state**: Not covered
- **Proposed state**: Add `user-invocable` (boolean, default `true`) -- set false to hide skill from slash menu (model-only invocation).
- **Sources**: Feature map "Skills > Frontmatter Fields" (docs)
- **Reasoning**: Important for skills that should only be triggered by the model, not manually by users.

---

### [Missing `effort` frontmatter for commands]
- **Type**: outdated
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/command-development/SKILL.md`
- **Current state**: The main SKILL.md does not list `effort` in its frontmatter section (though `references/frontmatter-reference.md` does cover it)
- **Proposed state**: Add `effort` to the SKILL.md frontmatter fields section for discoverability.
- **Sources**: Feature map "Commands > Frontmatter Fields" (`effort` field, v2.1.80)
- **Reasoning**: The frontmatter reference has it, but the primary SKILL.md that users read first does not.

---

### [Missing `/reload-plugins` command documentation]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/plugin-structure/SKILL.md`
- **Current state**: States "No restart required: Changes take effect on next Claude Code session" in auto-discovery section, but does not mention `/reload-plugins`
- **Proposed state**: Document `/reload-plugins` -- reloads all plugins mid-session without restart.
- **Sources**: Feature map "Plugin Management" (docs)
- **Reasoning**: Contradicts the existing "next session" guidance. `/reload-plugins` enables mid-session reloading.

---

### [Missing `lspServers` in plugin.json field documentation]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/plugin-structure/references/manifest-reference.md`
- **Current state**: Manifest reference documents `commands`, `agents`, `hooks`, `mcpServers` but omits `lspServers` and `skills` as explicit plugin.json fields
- **Proposed state**: Add `lspServers` (object, optional) -- LSP server definitions (inline only). Add `skills` (string | string[], optional, default `"./skills"`) to the component path fields section.
- **Sources**: Feature map "plugin.json Schema Fields" (`lspServers`, `skills` fields, docs)
- **Reasoning**: The manifest reference is incomplete. While the LSP skill exists separately, the manifest reference should list all valid plugin.json fields.

---

### [Missing OAuth configuration for MCP]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/mcp-integration/SKILL.md`
- **Current state**: OAuth mentioned only in passing ("OAuth flows handled automatically")
- **Proposed state**: Document the `oauth` field in MCP server config: `{ "authServerMetadataUrl": "..." }`. Also note MCP OAuth supports RFC 9728, CIMD/SEP-991, and Dynamic Client Registration (v2.1.81).
- **Sources**: Feature map "MCP Configuration > .mcp.json Schema" and "Key Features" (docs, v2.1.81)
- **Reasoning**: The explicit `oauth` configuration field is documented in the feature map schema but absent from plugin-dev.

---

### [Missing MCP env vars for headersHelper]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/mcp-integration/SKILL.md`
- **Current state**: Not covered
- **Proposed state**: Document `CLAUDE_CODE_MCP_SERVER_NAME` and `CLAUDE_CODE_MCP_SERVER_URL` env vars available in headersHelper scripts (v2.1.85).
- **Sources**: Feature map "MCP Configuration > Key Features" (v2.1.85)
- **Reasoning**: New in v2.1.85, useful for plugins that use headersHelper for authentication.

---

### [Missing plugin MCP deduplication with org connectors]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/mcp-integration/SKILL.md`
- **Current state**: Not covered
- **Proposed state**: Note that plugin MCP servers duplicating org-managed connectors are suppressed (v2.1.82). Plugin authors should be aware their MCP servers may not load if the org already provides the same connector.
- **Sources**: Feature map "MCP Configuration > Key Features" (v2.1.82)
- **Reasoning**: Important operational detail for enterprise plugin authors.

---

### [Outdated name length constraint in manifest reference]
- **Type**: outdated
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/plugin-structure/references/manifest-reference.md`
- **Current state**: Does not specify character length for plugin name
- **Proposed state**: Add "3-50 chars" constraint to match the feature map's plugin.json schema
- **Sources**: Feature map "plugin.json Schema Fields" (`name` field: "kebab-case, 3-50 chars")
- **Reasoning**: The feature map specifies an explicit character range. The manifest reference should include this constraint.

---

### [Missing `--plugin-dir` override behavior]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/plugin-structure/SKILL.md`
- **Current state**: Not covered
- **Proposed state**: Document that `--plugin-dir ./path` loads a plugin for the session only, can be repeated, and local `--plugin-dir` overrides installed marketplace plugin of same name (except managed).
- **Sources**: Feature map "Plugin Management" (docs)
- **Reasoning**: Key developer workflow for testing plugins during development.

---

### [Missing Elicitation in MCP documentation]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/mcp-integration/SKILL.md`
- **Current state**: Not covered
- **Proposed state**: Document MCP Elicitation -- servers can request structured user input mid-task. Related hook events: `Elicitation`, `ElicitationResult`.
- **Sources**: Feature map "MCP Configuration > Key Features" (docs)
- **Reasoning**: Elicitation is a significant MCP feature that enables interactive server-user communication.

---

### [plugin-validator agent references WebSocket transport]
- **Type**: deprecated
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/agents/plugin-validator.md`
- **Current state**: Validation step 8 checks "sse/http/ws: has `url` field" and security check mentions "HTTPS/WSS"
- **Proposed state**: Remove `ws` references. Change to "sse/http: has `url` field" and "HTTPS" only.
- **Sources**: Feature map "MCP Configuration > Transport Types" (no WebSocket)
- **Reasoning**: Consistent with removing fabricated WebSocket transport throughout.

---

### [Missing `statusMessage` hook field]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/hook-development/SKILL.md`
- **Current state**: Not covered in the hook handler fields
- **Proposed state**: Document `statusMessage` (string, optional) -- custom spinner message shown while hook is executing.
- **Sources**: Feature map "Common Handler Fields" (docs)
- **Reasoning**: Useful UX improvement for hooks that take time to execute.

---

### [Missing `async` field for command hooks]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/hook-development/SKILL.md`
- **Current state**: Not covered
- **Proposed state**: Document that command-type hooks support an `async` field and a `shell` field (`bash`/`powershell`).
- **Sources**: Feature map "Hook Handler Types" (command type key fields)
- **Reasoning**: The `async` field allows non-blocking hook execution. The `shell` field enables cross-platform hooks.

---

### [Missing SessionStart matcher values]
- **Type**: missing
- **Confidence**: high
- **Target file(s)**: `plugins/plugin-dev/skills/hook-development/SKILL.md`
- **Current state**: SessionStart shown with `"matcher": "*"` only
- **Proposed state**: Document specific matcher targets: `startup`, `resume`, `clear`, `compact`. These allow hooks to differentiate between fresh starts and resumes.
- **Sources**: Feature map "Hook Events" (SessionStart matcher targets, docs)
- **Reasoning**: Enables important use cases like running setup only on fresh sessions, not resumes.

---

## Summary

| Type | Count |
|------|-------|
| Missing | 24 |
| Outdated | 4 |
| Deprecated | 2 |
| **Total** | **30** |

### Priority Tiers

**Tier 1 -- Incorrect information (fix immediately):**
1. WebSocket transport removal (fabricated, 2 files)
2. Hook timeout defaults correction (factual error)
3. SSE deprecation in SKILL.md (actively misleading)

**Tier 2 -- Major missing features (high impact):**
4. 16 missing hook events
5. `http` and `agent` hook handler types
6. `${CLAUDE_PLUGIN_DATA}` variable
7. `if` conditional field for hooks (v2.1.85)
8. Agent frontmatter: `effort`, `maxTurns`, `disallowedTools`
9. MCP Elicitation and OAuth config
10. `/reload-plugins` command

**Tier 3 -- Minor missing features (moderate impact):**
11. `outputStyles` plugin.json field
12. `settings.json` in directory structure
13. `CLAUDE_CODE_PLUGIN_SEED_DIR`
14. Skill description 250-char cap
15. `user-invocable` skill field
16. `statusMessage`, `async`, `shell`, `once` hook fields
17. SessionStart matcher values
18. MCP env vars and dedup behavior
19. `--plugin-dir` override behavior
20. `lspServers`/`skills` in manifest reference
