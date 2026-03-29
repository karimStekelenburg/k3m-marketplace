---
description: Update the root CHANGELOG.md with recent changes across the marketplace. Use when changes have been applied to plugins, after optimization passes, or before releases.
argument-hint: "[plugin-name|all] [--since YYYY-MM-DD]"
---

# Update Changelog

Maintain the marketplace-wide `CHANGELOG.md` at the repository root. This file
tracks notable changes across all plugins in the marketplace.

## Input

$ARGUMENTS can be:
- A plugin name (e.g., `plugin-dev`) — document recent changes for that plugin
- `all` or empty — scan all plugins for undocumented changes
- `--since YYYY-MM-DD` — only include changes after this date

## Process

### Step 0: Set up worktree

All changelog work happens in an isolated worktree to keep main clean:

```bash
BRANCH="docs/changelog-$(date +%Y-%m-%d-%H%M%S)"
WORKTREE="/tmp/k3m-changelog-$$"
git worktree add -b "$BRANCH" "$WORKTREE" main
cd "$WORKTREE"
```

### Step 1: Determine what changed

Gather changes from git history on main:

```bash
git log main --oneline --since="${SINCE_DATE:-last tag or last changelog entry}" -- plugins/
```

Group commits by plugin. Ignore commits that only touch data/cache files.

### Step 2: Read existing changelog

Read `CHANGELOG.md` at the repository root. If it doesn't exist, create it with
this header:

```markdown
# Changelog

All notable changes to the K3M marketplace are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).
```

### Step 3: Determine the current date section

Check if a section for today's date already exists. If so, append to it.
Otherwise, create a new section:

```markdown
## YYYY-MM-DD
```

### Step 4: Categorize and write entries

For each plugin with changes, add entries under the date section grouped by type:

```markdown
## YYYY-MM-DD

### plugin-dev
- **Added**: Hook `http` and `agent` handler types documentation
- **Fixed**: Hook timeout defaults corrected from 60s to 600s
- **Removed**: Fabricated WebSocket MCP transport

### marketplace-maintenance
- **Added**: Changelog maintenance command
```

Use these categories:
- **Added** — new features, documentation, or components
- **Changed** — updates to existing content
- **Fixed** — corrections to incorrect information
- **Removed** — deprecated or deleted content

### Step 5: Commit, push, and create PR

```bash
git add CHANGELOG.md
git commit -m "docs(changelog): update for YYYY-MM-DD"
git push -u origin "$BRANCH"
gh pr create --title "docs: update changelog for YYYY-MM-DD" --body "Auto-generated changelog update for recent marketplace changes."
```

### Step 6: Clean up worktree

```bash
cd -
git worktree remove "$WORKTREE"
```

Report the PR URL to the user.

## Key Principles

1. **Concise.** One line per change, written from the user's perspective.
2. **Grouped by plugin.** Each plugin gets its own subsection under the date.
3. **Idempotent.** Running twice on the same day merges, doesn't duplicate.
4. **Append-only.** Never modify or remove historical entries.
5. **Isolated.** Always work in a worktree, never commit directly to main.
