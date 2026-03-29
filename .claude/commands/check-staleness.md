---
description: Check whether a plugin's reference documentation might be outdated by comparing timestamps against Claude Code release history. Use when checking if plugins need updating.
---

# Check Staleness

Determine whether a plugin's reference documentation might be outdated by comparing its `last_fetched` timestamps against known changelog activity.

## Input

$ARGUMENTS can be:
- A plugin name (e.g., `plugin-dev`) — checks that specific plugin
- `all` or empty — checks all plugins in the marketplace
- A path to an `index.yaml` file — checks that specific index

## Process

### Step 1: Locate reference doc indexes

Find `index.yaml` files to check:
- If a plugin name is given, look in `{marketplace_root}/plugins/{name}/references/index.yaml` and also check `{marketplace_root}/shared/*/index.yaml` if the plugin has a symlink to shared/
- If `all`, scan all plugins and the shared directory
- If a path, use that directly

### Step 2: Read changelog sources

Each `index.yaml` lists `changelog_sources`. Fetch the primary changelog URL (e.g., `https://code.claude.com/docs/en/changelog`) and extract recent entries.

Parse entries for:
- Date of each entry
- Topics mentioned (hooks, plugins, skills, agents, MCP, LSP, etc.)
- Whether the entry describes new features, breaking changes, or documentation updates

### Step 3: Compare timestamps

For each source in the index:
- If `last_fetched` is null → **STALE** (never fetched)
- If `last_fetched` is older than the newest relevant changelog entry → **POTENTIALLY STALE**
- If `last_fetched` is newer than all relevant changelog entries → **CURRENT**

"Relevant" means the changelog entry mentions topics covered by the source's `description` field.

### Step 4: Report findings

```
## Staleness Report for {plugin/scope}

### STALE (never fetched)
- hooks-reference: "Detailed hooks documentation..." (last_fetched: null)
- skills-reference: "Skills authoring..." (last_fetched: null)

### POTENTIALLY STALE (changelog activity since last fetch)
- plugins-reference: last fetched 2026-03-27, changelog entry on 2026-04-15 mentions "new plugin manifest fields"

### CURRENT
- marketplace-reference: last fetched 2026-03-27, no relevant changelog activity since

### Summary
2 sources never fetched, 1 potentially stale, 1 current.
Run `/update-refs {plugin}` to update stale references.
```

### Step 5: Handle errors gracefully

- If a changelog URL fails to fetch, report the error and skip timestamp comparison for that changelog source. Note that manual inspection may be needed.
- If an index.yaml is malformed, report the parsing error and skip that index.
- If the documentation index (llms.txt) is available, use it to verify that source URLs are still valid.

## Key principle

This command is **read-only and diagnostic**. It never modifies files. It tells you what might be stale and recommends next steps. The actual updating happens via `/update-refs`.
