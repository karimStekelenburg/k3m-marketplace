# K3M Marketplace — Step 1 Audit Report

**Date:** 2026-03-27
**Scope:** Inventory of `~/dev/k3m-marketplace` contents + comparison of installed plugin-dev (v0.1.0) against current Claude Code plugin documentation and Anthropic's skill-creator plugin.

---

## 1. Marketplace Inventory

The mounted marketplace folder contains **one file**:

| File | Purpose |
|------|---------|
| `k3m-marketplace-prd.md` | Product Requirements Document |

No plugins, no git repository, no shared reference docs, no registry, no feedback storage. The PRD references "a cloned plugin-dev plugin with partial updates" and "an in-progress meta-dev plugin concept," but these are not present in the mounted directory. They may exist elsewhere on the local machine.

**Conclusion:** The marketplace is effectively a blank slate with a PRD. All infrastructure described in the execution plan needs to be built from scratch.

---

## 2. Installed Plugin-Dev Plugin (v0.1.0)

**Source:** `claude-code-plugins` marketplace (Anthropic's official repo, authored by Daisy Hollman)
**Location:** `.local-plugins/cache/claude-code-plugins/plugin-dev/0.1.0/`

### Component Inventory

**Skills (7):**

| Skill | Word Count (est.) | References | Examples | Scripts |
|-------|-------------------|------------|----------|---------|
| plugin-structure | Standard | 2 (component-patterns, manifest-reference) | 3 (minimal, standard, advanced plugin) | — |
| command-development | Standard | 7 (plugin-features, frontmatter, marketplace, docs, advanced, testing, interactive) | 2 (simple-commands, plugin-commands) | — |
| skill-development | Standard | 1 (skill-creator-original) | — | — |
| hook-development | Standard | 3 (patterns, migration, advanced) | 3 (validate-write.sh, load-context.sh, validate-bash.sh) | 3 (validate-hook-schema.sh, test-hook.sh, hook-linter.sh) |
| mcp-integration | Standard | 3 (authentication, server-types, tool-usage) | 2 (stdio-server.json, http-server.json) | — |
| plugin-settings | Standard | 2 (real-world-examples, parsing-techniques) | 3 (example-settings.md, read-settings-hook.sh, create-settings-command.md) | 2 (validate-settings.sh, parse-frontmatter.sh) |
| agent-development | (not fully read) | (present) | (present) | — |

**Agents (3):** agent-creator, skill-reviewer, plugin-validator

**Commands (1):** create-plugin

**Hooks:** None

**MCP servers:** None

---

## 3. Comparison: Plugin-Dev vs. Current Official Documentation

Official reference: https://code.claude.com/docs/en/plugins-reference (fetched 2026-03-27)

### 3.1 Hook Events — SIGNIFICANTLY OUTDATED

Plugin-dev documents **9 hook events**. The official docs now list **22 events**.

| Event | In Plugin-Dev | Status |
|-------|:---:|--------|
| PreToolUse | ✅ | Current |
| PostToolUse | ✅ | Current |
| UserPromptSubmit | ✅ | Current |
| Stop | ✅ | Current |
| SubagentStop | ✅ | Current |
| SessionStart | ✅ | Current |
| SessionEnd | ✅ | Current |
| PreCompact | ✅ | Current |
| Notification | ✅ | Current |
| PermissionRequest | ❌ | **Missing** — fires when permission dialog appears |
| PostToolUseFailure | ❌ | **Missing** — fires after tool call fails |
| SubagentStart | ❌ | **Missing** — fires when subagent spawns |
| TaskCreated | ❌ | **Missing** — fires when task created via TaskCreate |
| TaskCompleted | ❌ | **Missing** — fires when task marked complete |
| StopFailure | ❌ | **Missing** — fires on API error turn end |
| TeammateIdle | ❌ | **Missing** — fires in agent teams when teammate idles |
| InstructionsLoaded | ❌ | **Missing** — fires when CLAUDE.md or rules loaded |
| ConfigChange | ❌ | **Missing** — fires when config file changes |
| CwdChanged | ❌ | **Missing** — fires on working directory change |
| FileChanged | ❌ | **Missing** — fires when watched file changes (matcher = filename) |
| WorktreeCreate | ❌ | **Missing** — fires when worktree created |
| WorktreeRemove | ❌ | **Missing** — fires when worktree removed |
| PostCompact | ❌ | **Missing** — fires after compaction completes |
| Elicitation | ❌ | **Missing** — fires on MCP elicitation request |
| ElicitationResult | ❌ | **Missing** — fires after user responds to elicitation |

### 3.2 Hook Type "agent" — MISSING

Official docs list 4 hook types: `command`, `http`, `prompt`, **`agent`** (agentic verifier with tools). Plugin-dev only documents the first three.

### 3.3 LSP Servers — ENTIRELY MISSING

The official docs describe a complete LSP (Language Server Protocol) integration system for real-time code intelligence. Plugin-dev has zero coverage of this feature:
- `.lsp.json` configuration format
- `lspServers` field in plugin.json
- Required fields (command, extensionToLanguage)
- Optional fields (transport, env, initializationOptions, settings, etc.)

### 3.4 ${CLAUDE_PLUGIN_DATA} — MISSING

Official docs introduce `${CLAUDE_PLUGIN_DATA}`, a persistent directory that survives plugin updates. Plugin-dev only covers `${CLAUDE_PLUGIN_ROOT}`. This is significant because:
- It resolves to `~/.claude/plugins/data/{id}/`
- Intended for node_modules, venvs, caches, generated code
- Has a recommended pattern for dependency management via SessionStart hooks
- Auto-deleted on uninstall (with `--keep-data` override)

### 3.5 userConfig — MISSING

Official docs describe `userConfig` in plugin.json for values prompted at plugin enable time:
- Supports `sensitive` flag (keychain storage) and non-sensitive (settings.json)
- Available as `${user_config.KEY}` substitution in MCP/LSP configs, hook commands
- Exported as `CLAUDE_PLUGIN_OPTION_<KEY>` env vars

### 3.6 Channels — MISSING

Official docs describe a `channels` field for message injection (Telegram/Slack/Discord style):
- Binds to plugin MCP servers
- Supports per-channel userConfig

### 3.7 Output Styles — MISSING

The official directory structure includes `output-styles/` and `outputStyles` in plugin.json. Not documented in plugin-dev.

### 3.8 Plugin-Level settings.json — MISSING

Official docs mention a `settings.json` at plugin root for default configuration applied at enable time (currently supports `agent` settings).

### 3.9 Plugin Manifest Fields — PARTIALLY OUTDATED

Plugin-dev's manifest-reference.md likely covers basic fields. Official docs add:
- `homepage`, `repository`, `license`, `keywords` (metadata)
- `outputStyles`, `lspServers`, `userConfig`, `channels` (component paths)
- Path behavior rules (custom paths replace defaults, must start with `./`)
- Array syntax for multiple component paths

### 3.10 Plugin Caching and File Resolution — MISSING

Official docs explain the plugin cache system (`~/.claude/plugins/cache`), path traversal limitations, and symlink workaround for external dependencies. Important for self-update mechanisms.

### 3.11 CLI Commands — NOT VERIFIED

Official docs cover: `plugin install`, `plugin uninstall` (with `--keep-data`), `plugin enable`, `plugin disable`, `plugin update`. Plugin-dev's coverage not verified but likely incomplete on newer flags.

---

## 4. Comparison: Skill-Creator Evaluation Infrastructure

Plugin-dev includes `references/skill-creator-original.md` which is a **direct copy** of Anthropic's skill-creator SKILL.md. The content covers:
- Skill anatomy and progressive disclosure
- 6-step creation process (understand → plan → initialize → edit → package → iterate)
- Writing style guidelines
- Validation checklist

**What's MISSING for the marketplace's evaluation needs:**
- **No train/test splitting infrastructure.** The PRD (FR10) calls for "train/test splitting for skill description evaluation." Neither the skill-creator original nor plugin-dev's skill-development skill includes this.
- **No A/B testing for descriptions.** The PRD (FR15) calls for comparing current vs. proposed skill descriptions. No infrastructure exists.
- **No `init_skill.py` or `package_skill.py`.** The skill-creator references these scripts, but they aren't present in plugin-dev (by design — plugin-dev uses direct directory creation instead).
- **No evaluation metrics or reporting.** No mechanism to measure whether a skill description triggers correctly across a set of test prompts.

**Conclusion:** Evaluation infrastructure needs to be built from scratch. The skill-creator provides the creation methodology but not the testing/evaluation tooling the PRD envisions.

---

## 5. Summary of Gaps

### Critical (blocks core marketplace functionality)

1. **13 missing hook events** — plugins created by plugin-dev won't know about FileChanged, WorktreeCreate, TaskCreated, etc.
2. **Missing ${CLAUDE_PLUGIN_DATA}** — plugins can't properly manage persistent state across updates
3. **Missing userConfig** — plugins can't prompt users for configuration at enable time
4. **Missing LSP servers** — entire component type not documented
5. **No evaluation infrastructure** — can't test or measure skill description quality

### Important (affects plugin quality)

6. **Missing hook type "agent"** — can't create agentic verification hooks
7. **Missing output styles** — component type not documented
8. **Missing channels** — component type not documented
9. **Missing plugin caching docs** — critical for understanding self-update limitations
10. **Missing plugin-level settings.json** — can't set default agent configs

### Nice-to-have (completeness)

11. Manifest metadata fields (homepage, repository, license, keywords)
12. CLI command flags (--keep-data, scope options)
13. Path behavior rules for custom component locations

---

## 6. Recommendations for Execution Plan

**For Step 2 (Organizational Strategy):** The marketplace is a blank slate — no existing organizational debt to resolve. Design conventions cleanly.

**For Step 3 (Meta-Dev Plugin):** Build from scratch. No existing meta-dev code to salvage.

**For Step 4 (Update Plugin-Dev):** The installed plugin-dev is Anthropic's official version. Rather than modifying the cached copy, the K3M marketplace should contain its own fork/version of plugin-dev that:
- Incorporates all 22 hook events
- Adds LSP, output styles, channels, userConfig documentation
- Adds ${CLAUDE_PLUGIN_DATA} coverage
- Converts reference docs to the index-and-fetch pattern
- Adds staleness metadata
- Builds evaluation infrastructure from scratch

**For Steps 6-7 (Feedback System):** No existing infrastructure. Build from scratch per conventions defined in Step 2.
