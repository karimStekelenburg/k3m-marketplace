---
name: plugin-development
description: >-
  This skill should be used when the user asks to "create a plugin",
  "scaffold a plugin", "understand plugin structure", "organize plugin
  components", "set up plugin.json", "configure plugin settings",
  "add LSP server", "configure language server", or needs guidance on
  plugin architecture, directory layout, manifest configuration,
  auto-discovery, or portable path references.
version: 0.3.0
---

# Plugin Development

Create, scaffold, and configure Claude Code plugins — directory layout, manifest, settings, LSP integration, and auto-discovery.

## Grounding Rule (MANDATORY)

Before answering ANY question about Claude Code plugin capabilities, syntax, or configuration:

1. **Discover doc pages**: Run `firecrawl map https://code.claude.com/docs/en/` to see all available pages (optionally add `--search "<topic>"` to narrow)
2. **Fetch the content**: Run `firecrawl scrape <url> -f markdown -o .firecrawl/<topic>.md` to get the full page
3. **Read the fetched content**: Use Read tool on the output file, then answer based on what the docs actually say
4. **Never** answer from memory alone when the question involves what Claude Code supports or how it works
5. **Never** hardcode doc URLs — always discover them fresh

Key doc pages to search for: `plugins`, `plugins-reference`, `claude-directory`, `settings`, `output-styles`

## Plugin Directory Structure

A plugin is a directory with `.claude-plugin/plugin.json` at minimum:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Required: at minimum {"name": "plugin-name"}
├── commands/                 # Slash commands (.md files) — auto-discovered
├── agents/                   # Subagent definitions (.md files) — auto-discovered
├── skills/                   # Skills (subdirectories with SKILL.md) — auto-discovered
├── hooks/
│   └── hooks.json           # Event handler configuration
├── .mcp.json                # MCP server definitions
├── .lsp.json                # LSP server definitions
└── output-styles/           # Output style definitions (.md files)
```

Components are auto-discovered. Only declare paths in plugin.json to override defaults.

## Portable Path References

- `${CLAUDE_PLUGIN_ROOT}` — resolves to the plugin's install directory at runtime. Use in hooks, MCP configs, and scripts.
- `${CLAUDE_PLUGIN_DATA}` — persistent plugin state directory that survives updates.
- `${CLAUDE_CODE_PLUGIN_SEED_DIR}` — original plugin source directory (for development).

## Plugin Settings Pattern

Plugins can store per-project configuration via `.claude/<plugin-name>.local.md`:

- YAML frontmatter for structured key-value settings
- Markdown body for freeform notes
- Gitignored (user-specific, not committed)
- Read from hooks via bash `awk` frontmatter extraction

## LSP Integration

Add `.lsp.json` at plugin root or `lspServers` in plugin.json. Key points:
- Configure connection only — don't bundle the server binary
- Document required binary installation in README
- Use `restartOnCrash: true` for reliability

**Always fetch current docs before advising on LSP configuration.**

## Development Workflow

1. Create directory with `.claude-plugin/plugin.json`
2. Add components (commands/, agents/, skills/, hooks/, .mcp.json, .lsp.json)
3. Test with `--plugin-dir /path/to/plugin` (development override)
4. Run `/reload-plugins` for hot reload during development
5. Validate: `claude plugin validate .`

## Marketplace-Specific Rules

- Plugin names: plain kebab-case, no `k3m-` prefix
- Register in `../../.claude-plugin/marketplace.json`
- All paths in plugin.json start with `./`
- Natural language files (SKILL.md, agents, commands) are code — see `docs/file-roles-and-dependencies.md`
