---
name: resource-management
description: Use when user wants to This skill should be used when the user asks to "add a resource", "update resources", "check resource status", "add a documentation source", "add a Twitter account to track", or needs to manage the plugin-dev-sync resource list. Provides guidance for maintaining the master resources.json that drives the discovery pipeline.
  This skill should be used when the user asks to "add a resource", "update resources",
  "check resource status", "add a documentation source", "add a Twitter account to track",
  or needs to manage the plugin-dev-sync resource list. Provides guidance for maintaining
  the master resources.json that drives the discovery pipeline.
---

# Resource Management

Maintain the master resource list at `data/resources.json` that drives plugin-dev-sync's
discovery and sync pipeline. Every resource the system crawls must be registered here.

## Resource File Location

The resource file lives at `${CLAUDE_PLUGIN_ROOT}/data/resources.json`.

## Resource Schema

Each resource entry has these fields:

| Field | Required | Description |
|-------|----------|-------------|
| `id` | yes | Unique kebab-case identifier |
| `url` | yes | Fetchable URL |
| `name` | yes | Human-readable label |
| `category` | yes | One of: `official-docs`, `github`, `social`, `community` |
| `type` | yes | One of: `page`, `sitemap-root`, `repo`, `releases`, `directory`, `twitter`, `rss`, `api` |
| `notes` | no | Context for crawlers — what to look for |
| `status` | yes | `active` or `inactive` |

## Adding a Resource

1. Read current `data/resources.json`
2. Verify the URL is reachable: `curl -sI <url>`
3. Assign an `id` following the pattern: `<category>-<short-name>` (e.g., `docs-hooks`, `twitter-karpathy`)
4. Add the entry to the `resources` array
5. Test with: `uv run ${CLAUDE_PLUGIN_ROOT}/scripts/fetch-resources.py --id <new-id>`
6. Verify the cached content is useful

## Removing or Deactivating a Resource

Prefer setting `"status": "inactive"` over deleting, to preserve history.
Only delete entries that were added by mistake.

## Validating Resources

Run the fetch script to check all resources are reachable:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/fetch-resources.py
```

Review `data/fetch-report.json` for failures. Common issues:
- URL changed → update the URL
- Page removed → mark inactive, find replacement
- Rate limited → add notes about rate limits

## Categories

- **official-docs**: Anthropic documentation pages (docs.anthropic.com)
- **github**: Repositories, releases, directories on GitHub
- **social**: Twitter/X accounts, announcement channels
- **community**: Blog posts, tutorials, third-party guides

## Fetch Script

The fetch script at `scripts/fetch-resources.py` supports filtering:

```bash
# Fetch everything
uv run scripts/fetch-resources.py

# Fetch one category
uv run scripts/fetch-resources.py --category official-docs

# Fetch one resource
uv run scripts/fetch-resources.py --id docs-claude-code-hooks
```

Results are cached in `data/cache/<id>.txt` and summarized in `data/fetch-report.json`.
