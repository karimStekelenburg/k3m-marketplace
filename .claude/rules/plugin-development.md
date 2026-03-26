---
globs: plugins/**
---

# Plugin Development Rules

When working on plugins in this marketplace:

1. Always validate with `claude plugin validate .` before committing
2. Register new plugins in `../../.claude-plugin/marketplace.json`
3. Use `${CLAUDE_PLUGIN_ROOT}` for all internal path references
4. Keep plugin.json minimal — only `name` is required, rely on auto-discovery
5. Plugin names must be plain kebab-case — no `k3m-` prefix (the marketplace namespace already implies ownership)
6. Test plugins by installing the marketplace locally:
   ```
   /plugin marketplace add /path/to/k3m-marketplace
   ```
