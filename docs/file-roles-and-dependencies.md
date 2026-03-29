# File Roles and Dependencies in an LLM-Native Codebase

## Why This Document Exists

In a traditional codebase, "code" means executable files and "documentation" is
supplementary material that can be changed without breaking anything.

**This repository is not traditional.** It is a Claude Code plugin marketplace
where natural language IS code. A SKILL.md is a program. An agent `.md` file is
a program. A `references/patterns.md` file is a dependency of that program. They
define the behavior of Claude Code agents the same way functions and classes
define behavior in compiled software.

Removing a reference file that a SKILL.md points to is equivalent to deleting a
module that a Python script imports. It will break.

This document is referenced from `.claude/CLAUDE.md` and is therefore part of
Claude's active context. Every contributor (human or AI agent) MUST understand
these rules before adding, modifying, or removing files.

## The Two Worlds

Every file in this repository belongs to exactly one of two worlds:

### World 1: Agent-Facing (Claude will read these)

Files that Claude Code discovers, loads, or follows references to. These are
**code** — they define agent behavior and have real dependencies.

This includes:
- **Entry points**: files Claude Code auto-discovers (`CLAUDE.md`, `SKILL.md`,
  `agents/*.md`, `commands/*.md`, `hooks.json`, `.mcp.json`, `plugin.json`,
  `marketplace.json`, `settings.json`, `.claude/rules/*.md`)
- **Referenced files**: files that entry points or other referenced files point
  to (`references/*.md`, `examples/*.md`, `scripts/*.sh`, `shared/`, etc.)
- **Data files**: files that agent processes read or write (`registry.yaml`,
  `data/resources.json`, `data/cache/*.txt`, etc.)

### World 2: Human-Facing (Claude will NOT read these)

Files written for human audiences. These live in `docs/human/` and Claude's
read access to this directory is denied via `filesystem.denyRead` in
`.claude/settings.json`.

This includes:
- `README.md` files (installation guides, user-facing docs)
- Product requirements documents
- Architecture overviews written for human onboarding
- Audit reports
- Any other prose meant for human consumption

**The boundary is enforced, not advisory.** By denying read access, we guarantee
that human-facing docs cannot accidentally influence Claude's behavior, and that
Claude cannot develop dependencies on files meant for humans.

### Moving Between Worlds

If a human-facing document needs to become agent-facing (e.g., an architecture
doc that a skill should reference), move it OUT of `docs/human/` and INTO the
appropriate location in the agent-facing tree. Then add explicit references from
the relevant entry points.

If an agent-facing document is no longer referenced by any entry point or
referenced file, it MAY be moved to `docs/human/` — but verify first by
running:

```bash
grep -r "filename.md" --include="*.md" --include="*.json" --include="*.yaml" .
```

## How Agent-Facing Dependencies Work

### Entry Points

Claude Code auto-discovers these files at specific paths. They are the roots
of every dependency tree:

| File | Discovered by |
|------|--------------|
| `CLAUDE.md` / `.claude/CLAUDE.md` | Session start |
| `.claude/rules/*.md` | Session start |
| `.claude-plugin/marketplace.json` | Plugin loader |
| `<plugin>/.claude-plugin/plugin.json` | Plugin loader |
| `<plugin>/skills/*/SKILL.md` | Skill matcher |
| `<plugin>/agents/*.md` | Subagent spawner |
| `<plugin>/commands/*.md` | Slash-command handler |
| `<plugin>/hooks/hooks.json` | Hook runner |
| `<plugin>/.mcp.json` | MCP client |
| `<plugin>/.lsp.json` | LSP client |
| `<plugin>/settings.json` | Settings merger |

### Referenced Files

When Claude reads an entry point, it follows references to load additional
files. Those files may reference further files. This forms a dependency tree.

Claude loads `references/`, `examples/`, and `scripts/` subdirectories
**on demand** — it reads them when the parent skill/command/agent is triggered
and the content is relevant. But the files MUST exist at the referenced path,
or Claude will fail to find them.

### The `@` Syntax (Commands Only)

Commands support `@filename` syntax to include file contents inline:

```markdown
---
description: Review a file
argument-hint: [file-path]
---

Review @$1 for code quality and best practices.
```

- `@$1`, `@$2` — include contents of the Nth argument (a file path)
- `@path/to/file.json` — include contents of a specific file

This is a **command-only** feature. Skills and agents do not support `@` syntax;
they reference files by mentioning paths in their body text, which Claude then
reads via the Read tool.

## Linking Conventions

All agent-facing files MUST follow these conventions when referencing other
files, so that references are consistent, parseable, and traceable.

### 1. Always use backtick-quoted paths

```markdown
See `references/patterns.md` for common patterns.
```

Never write bare paths without backticks.

### 2. Always include the file extension

```markdown
See `references/patterns.md`       (correct)
See `references/patterns`          (wrong — ambiguous)
```

### 3. Use relative paths within a skill/component

For files in the same skill directory tree:

```markdown
See `references/patterns.md` for common hook patterns.
See `examples/validate-write.sh` for a complete example.
Run `scripts/validate-hook-schema.sh` to check syntax.
```

### 4. Use `${CLAUDE_PLUGIN_ROOT}` for cross-component paths

For files in a different component of the same plugin:

```markdown
Run `${CLAUDE_PLUGIN_ROOT}/scripts/detect-backend.sh`
```

### 5. Use `${CLAUDE_PLUGIN_ROOT}/..` for sibling plugins

```markdown
Target: `${CLAUDE_PLUGIN_ROOT}/../plugin-dev`
```

### 6. Use marketplace-root-relative paths for shared resources

For files at the marketplace root (from commands or skills that operate on the
marketplace itself):

```markdown
Read `registry.yaml` from the marketplace root.
See `docs/cheatsheet-plugin.md` for the complete schema.
Check `shared/claude-code-platform/index.yaml`.
```

### 7. Group references in a dedicated section

At the end of every SKILL.md, agent, or command that references other files,
include a clearly labeled section:

```markdown
## References

- **`references/patterns.md`** — Common hook patterns (8+ proven patterns)
- **`references/migration.md`** — Migrating from basic to advanced hooks
- **`examples/validate-write.sh`** — Write validation example
- **`scripts/hook-linter.sh`** — Check hook scripts for common issues
```

Use bold backtick-quoted paths with a dash and description.

### 8. Describe what the reference contains

Don't just link — explain what the reader will find, so Claude can decide
whether to load the file:

```markdown
**`references/advanced.md`** — Advanced techniques including multi-hook
coordination, dynamic matcher generation, and cross-plugin hook patterns
```

## Before Removing or Renaming Any File

1. **Is it in `docs/human/`?** Safe to modify freely.
2. **Is it an entry point?** Do NOT remove unless decommissioning the component.
   Update `marketplace.json` or `plugin.json` accordingly.
3. **Is it referenced by an entry point or another referenced file?** Grep the
   entire repo. Update every referrer BEFORE removing.
4. **Is it a data/generated file?** Safe to remove if the generating process can
   recreate it.

```bash
# Quick dependency check
grep -r "filename" --include="*.md" --include="*.json" --include="*.yaml" .
```

## Summary

| World | Location | Claude access | Dependency rules |
|-------|----------|--------------|-----------------|
| Agent-facing | Everywhere except `docs/human/` | Full read | Must trace references before changes |
| Human-facing | `docs/human/` only | Denied via settings | Can modify freely |
