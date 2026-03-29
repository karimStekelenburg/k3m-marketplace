# k3m-marketplace — Marketplace Development Guide

## File Roles and Dependencies

**Read `docs/file-roles-and-dependencies.md` before adding, modifying, or removing any file.**

Key rules:
- Natural language files (SKILL.md, agents, commands, references) are **code**, not documentation
- Files in `docs/human/` are human-only — Claude's read access is denied via settings
- Before removing any file, check if it's referenced by an entry point or another referenced file
- Use backtick-quoted relative paths when referencing files (see linking conventions in the doc)
- Commands support `@filename` syntax to include file contents; skills do not

## Plugin Structure Rules

- Every plugin lives in `plugins/<plugin-name>/`
- Each plugin MUST have `.claude-plugin/plugin.json` with at least `"name"`
- Components (commands/, agents/, skills/, hooks/) go at plugin root, NOT inside `.claude-plugin/`
- All paths in plugin.json MUST start with `./`
- Plugin names MUST be kebab-case
- Every plugin in `plugins/` MUST be registered in `.claude-plugin/marketplace.json`

## Validation Rules

- `agents` field in plugin.json can be a string or array (both valid)
- `commands` and `skills` can be a directory string or array of paths
- `category` and `tags` belong in marketplace.json entries, NOT in plugin.json
- Use `${CLAUDE_PLUGIN_ROOT}` for all plugin-relative paths in hooks, MCP, and LSP configs
- Use `${CLAUDE_PLUGIN_DATA}` for persistent plugin state that survives updates

## Component Reference

See `docs/cheatsheet-*.md` for complete field references:
- `cheatsheet-plugin.md` — plugin.json schema
- `cheatsheet-skill.md` — SKILL.md frontmatter
- `cheatsheet-agent.md` — AGENT.md frontmatter
- `cheatsheet-hooks.md` — hooks.json schema
- `cheatsheet-mcp.md` — .mcp.json schema
- `cheatsheet-lsp.md` — .lsp.json / lspServers schema
- `cheatsheet-commands.md` — command .md frontmatter
- `cheatsheet-output-styles.md` — output style .md frontmatter

## Marketplace JSON

- Located at `.claude-plugin/marketplace.json`
- `strict: true` (default) — plugin.json is authority, marketplace entry supplements
- `strict: false` — marketplace entry is entire definition, plugin.json must NOT declare components
- `metadata.pluginRoot` is prepended to relative `source` paths

## Testing

```bash
claude plugin validate plugins/<plugin-name>
```
