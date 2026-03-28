---
name: sync
description: >-
  This skill should be used when the user asks to "sync plugin-dev",
  "update plugin-dev from latest docs", "run meta-dev sync", or invokes
  /meta-dev:sync. Orchestrates the full autonomous pipeline: fetch resources,
  discover features, diff against plugin-dev, review, apply patches, commit,
  and create a PR with a full report.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - WebFetch
  - WebSearch
argument-hint: "[--dry-run] [--category official-docs|github|social|community]"
---

# Sync Pipeline

Orchestrate a full autonomous sync of plugin-dev against the latest Claude Code
documentation and community resources. Every change is committed and submitted as
a PR with a detailed report.

## Pipeline Overview

```
fetch → discover → diff → review → worktree → apply → changelog → push → PR
```

## Step 1: Fetch Resources

Run the fetch script to update the local cache:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/fetch-resources.py
```

Read `data/fetch-report.json` to verify fetch success. If critical resources
failed (official-docs, github releases), abort and report the failures.

## Step 2: Discover Features

Launch the **discovery-crawler** agent to analyze cached content:

- Pass it the path to `data/cache/` and `data/resources.json`
- The agent reads cached pages, extracts features, settings, CLI flags,
  hook events, MCP capabilities, plugin schema fields, and behaviors
- Output: a structured feature map as a markdown report

The agent should cross-reference multiple sources. A feature mentioned in
release notes AND docs is high-confidence. A feature only on Twitter is
low-confidence and should be flagged.

## Step 3: Diff Against plugin-dev

Compare the discovered feature map against the current state of plugin-dev:

1. Read all files in the target plugin-dev directory (skills, agents, references)
2. Identify:
   - **Outdated**: Information in plugin-dev that contradicts current docs
   - **Missing**: Features/settings discovered that plugin-dev doesn't cover
   - **Deprecated**: Things plugin-dev documents that no longer exist
3. Produce a diff report with:
   - What to change and why
   - Source links for each change (which resource(s) informed it)
   - Confidence level (high/medium/low based on source count)

## Step 4: Independent Review

Launch the **diff-reviewer** agent with the diff report:

- The reviewer independently spot-checks claims against the cached sources
- Verifies that proposed changes are accurate
- Flags any changes that seem wrong or unsupported
- Returns an approved/rejected verdict per change with reasoning

Drop any changes the reviewer rejects. Log rejections in the PR report.

## Step 5: Apply, Commit, and PR

If there are approved changes (and not `--dry-run`):

### Step 5.1: Set up worktree

All sync work happens in an isolated worktree:

```bash
BRANCH="plugin-dev-sync/sync-YYYY-MM-DD-HHMMSS"
WORKTREE="/tmp/k3m-sync-$$"
git worktree add -b "$BRANCH" "$WORKTREE" main
cd "$WORKTREE"
```

### Step 5.2: Apply changes

1. Launch the **patch-applier** agent to apply each approved change
2. After each logical group of changes, commit with a descriptive message

### Step 5.3: Update plugin-dev changelog

After all plugin-dev changes are committed, update `plugins/plugin-dev/CHANGELOG.md`:

1. Read the existing changelog (or create it with this header if missing):

```markdown
# Changelog

All notable changes to plugin-dev are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).
```

2. Add a new date section (or append to today's if it already exists)
3. For each approved change that was applied, add a one-line entry categorized as:
   - **Added** — new documentation or features
   - **Changed** — updates to existing content
   - **Fixed** — corrections to incorrect information
   - **Removed** — deprecated or deleted content

Example:

```markdown
## 2026-03-28

- **Fixed**: Hook timeout defaults corrected from 60s to 600s
- **Removed**: Fabricated WebSocket MCP transport
- **Added**: 16 missing hook events documentation
- **Added**: `http` and `agent` hook handler types
```

4. Commit: `docs(plugin-dev): update changelog for sync YYYY-MM-DD`

### Step 5.4: Push and create PR

```bash
git push -u origin "$BRANCH"
gh pr create --title "fix(plugin-dev): sync against latest docs YYYY-MM-DD" --body "$(cat <<'EOF'
<PR body — see format below>
EOF
)"
```

### Step 5.5: Clean up worktree

```bash
cd -
git worktree remove "$WORKTREE"
```

Report the PR URL to the user.

### PR Body Format

```markdown
## Plugin-Dev Sync Report

**Date**: YYYY-MM-DD
**Resources fetched**: X/Y successful
**Changes proposed**: N
**Changes approved**: M (K rejected by reviewer)

## Changes Applied

### [Change Title]
- **Type**: outdated | missing | deprecated
- **Confidence**: high | medium | low
- **Files modified**: list of files
- **Sources**: [Source Name](url), [Source Name](url)
- **Reasoning**: Why this change was made

### ...

## Rejected Changes

### [Change Title]
- **Reason for rejection**: reviewer's reasoning
- **Sources checked**: ...

## Validation Results

- `claude plugin validate`: PASS/FAIL
- Skill trigger test: PASS/FAIL
- Agent YAML parse: PASS/FAIL
```

## Dry Run Mode

If `--dry-run` is passed, stop after Step 4 and print the approved diff
report without applying changes or creating a PR.

## Target Plugin-Dev Location

The default target is the sibling plugin-dev directory:
`${CLAUDE_PLUGIN_ROOT}/../plugin-dev`

## Error Handling

- If fetch fails for >50% of resources, abort with error report
- If no changes are found, report "plugin-dev is up to date" and exit
- If `claude plugin validate` fails after patching, revert the last change and retry
- Always ensure the branch is clean before creating the PR
