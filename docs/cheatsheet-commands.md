# Command .md — Complete Frontmatter Reference

Location: `<plugin-root>/commands/<command-name>.md`

Commands are user-invoked slash commands defined as Markdown files. The file content becomes instructions FOR Claude (not documentation for the user).

## Frontmatter Fields

### description
- **Type:** `string`
- **Purpose:** Brief description shown in `/help`
- **Default:** First line of command content
- **Example:** `description: Review code for security vulnerabilities`

### allowed-tools
- **Type:** `string` (comma-separated) or array
- **Purpose:** Restrict which tools the command can use
- **Default:** Inherits from conversation
- **Patterns:**
  - `Read, Write, Edit` — specific tools
  - `Bash(git:*)` — Bash limited to git commands
  - `mcp__plugin_name_server__*` — all tools from an MCP server
- **Example:** `allowed-tools: Read, Grep, Bash(git:*)`

### model
- **Type:** `string`
- **Options:** `sonnet`, `opus`, `haiku`
- **Default:** Inherits from conversation
- **Example:** `model: haiku`

### argument-hint
- **Type:** `string`
- **Purpose:** Document expected arguments (shown in autocomplete)
- **Example:** `argument-hint: [file-path] [severity]`

### disable-model-invocation
- **Type:** `boolean`
- **Default:** `false`
- **Purpose:** Prevent SlashCommand tool from programmatically calling this command
- **Example:** `disable-model-invocation: true`

## Dynamic Features

### Arguments

- `$ARGUMENTS` — all arguments as single string
- `$1`, `$2`, `$3` — positional arguments

```markdown
Fix issue #$1 with priority $2
```

Usage: `/fix-issue 123 high`

### File References

- `@path/to/file` — include file contents
- `@$1` — include file from argument

```markdown
Review @$1 for security issues
```

### Bash Execution

- `` !`command` `` — execute bash and include output

```markdown
Changed files: !`git diff --name-only`
```

## Naming Convention

- File name becomes command name: `review-pr.md` → `/review-pr`
- Subdirectories create namespaces: `ci/build.md` → `/build` (shown as `project:ci`)
- Use kebab-case, verb-noun pattern

## Gotchas

1. **Content is FOR Claude** — write instructions, not documentation
2. **No frontmatter needed** for simple commands
3. **`$ARGUMENTS` and `$1` are different** — `$ARGUMENTS` gets everything, `$1` gets first word
4. **Bash in commands requires `allowed-tools`** — include `Bash(...)` pattern
5. **`${CLAUDE_PLUGIN_ROOT}` available** — for referencing plugin resources

## Complete Example

```markdown
---
description: Review PR with security focus
allowed-tools: Read, Grep, Bash(git:*, gh:*)
argument-hint: [pr-number]
model: sonnet
---

PR details: !`gh pr view $1 --json title,body,files`

Review pull request #$1 with focus on:

1. Security vulnerabilities (OWASP Top 10)
2. Input validation and sanitization
3. Authentication/authorization issues
4. Sensitive data exposure

For each issue found, provide:
- **Severity:** Critical/High/Medium/Low
- **File:** path and line number
- **Issue:** clear description
- **Fix:** recommended remediation
```
