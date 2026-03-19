# plugin.json — Complete Field Reference

Location: `<plugin-root>/.claude-plugin/plugin.json`

## Fields

### name (required)
- **Type:** `string`
- **Format:** kebab-case, 3-50 chars, alphanumeric + hyphens, must start/end with alphanumeric
- **Example:** `"name": "code-review-assistant"`

### version
- **Type:** `string` (semver)
- **Example:** `"version": "1.2.0"`

### description
- **Type:** `string`
- **Example:** `"description": "Automated code review with security analysis"`

### author
- **Type:** `object`
- **Fields:** `name` (string), `email` (string), `url` (string)
- **Example:**
  ```json
  "author": {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "url": "https://example.com"
  }
  ```

### homepage
- **Type:** `string` (URL)
- **Example:** `"homepage": "https://github.com/user/plugin"`

### repository
- **Type:** `string` (URL)
- **Example:** `"repository": "https://github.com/user/plugin"`

### license
- **Type:** `string`
- **Example:** `"license": "MIT"`

### keywords
- **Type:** `string[]`
- **Example:** `"keywords": ["testing", "automation", "ci-cd"]`

### commands
- **Type:** `string | string[]`
- **Default:** `"./commands"` (auto-discovered)
- **Behavior:** Custom paths SUPPLEMENT default `commands/` directory, not replace
- **Example:** `"commands": ["./commands", "./extra-commands"]`

### agents
- **Type:** `string | string[]`
- **Default:** `"./agents"` (auto-discovered)
- **Behavior:** Custom paths SUPPLEMENT default `agents/` directory
- **Example:** `"agents": "./agents"` or `"agents": ["./agents", "./more-agents"]`

### skills
- **Type:** `string | string[]`
- **Default:** `"./skills"` (auto-discovered)
- **Behavior:** Custom paths SUPPLEMENT default `skills/` directory
- **Example:** `"skills": "./skills"`

### hooks
- **Type:** `string`
- **Default:** `"./hooks/hooks.json"` (auto-discovered)
- **Example:** `"hooks": "./config/hooks.json"`

### mcpServers
- **Type:** `string | object`
- **Default:** `./.mcp.json` (auto-discovered)
- **As string:** path to .mcp.json file
- **As object:** inline MCP server definitions
- **Example (inline):**
  ```json
  "mcpServers": {
    "my-server": {
      "command": "${CLAUDE_PLUGIN_ROOT}/server.js"
    }
  }
  ```

### lspServers
- **Type:** `object`
- **Example:**
  ```json
  "lspServers": {
    "typescript": {
      "command": "typescript-language-server",
      "args": ["--stdio"],
      "extensionToLanguage": {
        ".ts": "typescript",
        ".tsx": "typescriptreact"
      }
    }
  }
  ```

### outputStyles
- **Type:** `string | string[]`
- **Default:** `"./output-styles"` (auto-discovered)
- **Example:** `"outputStyles": "./styles"`

## Gotchas

1. **Only `name` is required** — everything else is optional
2. **Do NOT put `category` or `tags` here** — those go in marketplace.json
3. **All paths must start with `./`** — no absolute paths
4. **Custom paths supplement, not replace** — if `commands/` exists, its contents load too
5. **Auto-discovery is the default** — only specify paths for non-standard layouts
6. **Components go at plugin root** — NOT inside `.claude-plugin/`

## Minimal Example

```json
{
  "name": "my-plugin"
}
```

## Full Example

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "A comprehensive plugin example",
  "author": {
    "name": "Author Name",
    "email": "author@example.com",
    "url": "https://example.com"
  },
  "homepage": "https://github.com/user/my-plugin",
  "repository": "https://github.com/user/my-plugin",
  "license": "MIT",
  "keywords": ["productivity", "review"],
  "commands": "./commands",
  "agents": ["./agents"],
  "skills": "./skills",
  "hooks": "./hooks/hooks.json",
  "mcpServers": "./.mcp.json",
  "outputStyles": "./output-styles"
}
```
