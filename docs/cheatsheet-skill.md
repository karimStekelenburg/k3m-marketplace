# SKILL.md — Complete Frontmatter Reference

Location: `<plugin-root>/skills/<skill-name>/SKILL.md`

Skills are model-invoked capabilities that Claude autonomously activates based on task context. Unlike commands (user-invoked), skills activate automatically when the description matches the user's request.

## Frontmatter Fields

### name (required)
- **Type:** `string`
- **Format:** kebab-case identifier
- **Example:** `name: api-testing`

### description (required)
- **Type:** `string`
- **Purpose:** Tells Claude WHEN to invoke this skill — this is the trigger mechanism
- **Best practice:** Include specific trigger phrases, keywords, and topic areas
- **Example:**
  ```yaml
  description: >-
    This skill should be used when the user asks to "write tests for API endpoints",
    "test REST API", "validate API responses", or discusses API testing patterns.
    Provides comprehensive guidance for API testing.
  ```

### version (optional)
- **Type:** `string` (semver)
- **Example:** `version: 1.0.0`

### license (optional)
- **Type:** `string`
- **Example:** `license: MIT`

### allowed-tools (optional)
- **Type:** `string` (comma-separated)
- **Purpose:** Pre-allow specific tools without user permission prompts
- **Example:** `allowed-tools: Read, Grep, Bash(git:*)`

### argument-hint (optional)
- **Type:** `string`
- **Purpose:** Document expected arguments for autocomplete
- **Example:** `argument-hint: [file-path] [format]`

### model (optional)
- **Type:** `string`
- **Options:** `sonnet`, `opus`, `haiku`
- **Default:** Inherits from conversation

### disable-model-invocation (optional)
- **Type:** `boolean`
- **Default:** `false`
- **Purpose:** Prevent Claude from auto-invoking this skill

### user-invocable (optional)
- **Type:** `boolean`
- **Default:** `true`
- **Purpose:** Set `false` to hide from slash command menu (still auto-activatable)

## File Structure

```
skills/
└── my-skill/
    ├── SKILL.md          # Required — main skill definition
    ├── references/       # Optional — reference materials
    │   └── patterns.md
    ├── examples/         # Optional — example files
    │   └── sample.md
    └── scripts/          # Optional — helper scripts
        └── helper.sh
```

## Writing Effective Descriptions

The `description` is the most important field — it determines when Claude activates the skill.

**Pattern:**
```yaml
description: >-
  This skill should be used when the user asks to "phrase 1", "phrase 2",
  mentions "keyword", or discusses topic-area. Also trigger when working with
  specific-technology or solving problem-type.
```

**Include:**
- Specific trigger phrases users might say (in quotes)
- Keywords that indicate relevance
- Topic areas the skill covers
- Technologies or tools involved
- When NOT to use (to avoid false triggers)

## Body Content

The markdown body after frontmatter is the skill's knowledge/instructions. Structure it as:

1. **Overview** — what the skill helps with
2. **When to use** — activation conditions (reinforces description)
3. **Guidance** — structured knowledge, patterns, best practices
4. **Examples** — concrete, actionable examples
5. **References** — point to supporting files in subdirectories

## Gotchas

1. **File MUST be named `SKILL.md`** — not `README.md` or anything else
2. **Must be in a subdirectory** — `skills/my-skill/SKILL.md`, not `skills/my-skill.md`
3. **Description drives activation** — a vague description means the skill rarely fires
4. **Supporting files are accessible** — Claude can Read files in the skill's directory
5. **`${CLAUDE_PLUGIN_ROOT}` works in content** — reference plugin resources portably

## Complete Example

```markdown
---
name: database-migrations
description: >-
  This skill should be used when the user asks to "create a migration",
  "add a database column", "modify schema", "run migrations", or discusses
  database schema changes, Alembic, Prisma migrations, or Django migrations.
version: 1.0.0
---

# Database Migration Patterns

## Overview

This skill provides guidance for creating safe, reversible database migrations.

## Migration Checklist

1. Always create reversible migrations (include down/rollback)
2. Never drop columns in production without a deprecation period
3. Add new columns as nullable or with defaults
4. Create indexes concurrently to avoid table locks
5. Test migrations against a copy of production data

## Examples

### Adding a column (safe)
...

### Renaming a column (two-step)
...
```
