# .mcp.json — Complete Schema Reference

Location: `<plugin-root>/.mcp.json` or inline in `plugin.json` under `mcpServers`

MCP (Model Context Protocol) servers provide external tool integrations for Claude Code plugins.

## File Format

```json
{
  "<server-name>": {
    "type": "<transport-type>",
    ...transport-specific fields
  }
}
```

## Transport Types

### stdio (Local Process) — Default

Spawn a local process, communicate via stdin/stdout.

```json
{
  "my-server": {
    "command": "node",
    "args": ["${CLAUDE_PLUGIN_ROOT}/server.js", "--flag"],
    "env": {
      "API_KEY": "${API_KEY}",
      "LOG_LEVEL": "info"
    }
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | string | Yes | Executable to run |
| `args` | string[] | No | Command arguments |
| `env` | object | No | Environment variables |

**Notes:**
- `type` field can be omitted (stdio is default)
- Process managed by Claude Code (started/stopped automatically)
- Use `${CLAUDE_PLUGIN_ROOT}` for portable paths

### sse (Server-Sent Events)

Connect to a hosted MCP server with SSE transport. Supports OAuth.

```json
{
  "my-service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse"
  }
}
```

With OAuth:
```json
{
  "my-service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse",
    "oauth": {
      "clientId": "your-client-id",
      "callbackPort": 8080
    }
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Must be `"sse"` |
| `url` | string | Yes | SSE endpoint URL (HTTPS) |
| `oauth` | object | No | OAuth config (`clientId`, `callbackPort`) |

**Notes:**
- OAuth handled automatically by Claude Code
- User prompted on first use
- No local installation needed

### http (REST API)

Connect to a RESTful MCP server.

```json
{
  "api-service": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}",
      "X-Custom-Header": "value"
    }
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Must be `"http"` |
| `url` | string | Yes | API endpoint URL (HTTPS) |
| `headers` | object | No | Custom HTTP headers |

### ws (WebSocket)

Connect to a WebSocket MCP server for real-time communication.

```json
{
  "realtime": {
    "type": "ws",
    "url": "wss://mcp.example.com/ws",
    "headers": {
      "Authorization": "Bearer ${TOKEN}"
    }
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Must be `"ws"` |
| `url` | string | Yes | WebSocket URL (WSS) |
| `headers` | object | No | Custom headers |

## Environment Variable Expansion

All fields support `${VAR_NAME}` substitution:
- `${CLAUDE_PLUGIN_ROOT}` — plugin's install directory
- `${CLAUDE_PLUGIN_DATA}` — persistent data directory
- `${ANY_USER_ENV_VAR}` — from user's shell environment

## Tool Naming Convention

MCP tools are automatically namespaced:

```
mcp__plugin_<plugin-name>_<server-name>__<tool-name>
```

Example: Plugin `asana`, server `asana`, tool `create_task`:
```
mcp__plugin_asana_asana__asana_create_task
```

## Gotchas

1. **Always use HTTPS/WSS** — never HTTP/WS in production
2. **Never hardcode tokens** — use `${ENV_VAR}` references
3. **Document required env vars** in plugin README
4. **stdio is default type** — `"type"` field optional for stdio
5. **Servers connect on-demand** — not all start at session begin
6. **Use `/mcp` command** to verify servers are running
7. **Config changes need restart** — MCP config loads at session start
8. **Use `${CLAUDE_PLUGIN_ROOT}`** for all local server paths

## Complete Multi-Server Example

```json
{
  "local-db": {
    "command": "python3",
    "args": ["-m", "db_mcp_server"],
    "env": {
      "DATABASE_URL": "${DATABASE_URL}"
    }
  },
  "cloud-api": {
    "type": "sse",
    "url": "https://mcp.cloud-service.com/sse"
  },
  "internal-api": {
    "type": "http",
    "url": "https://internal.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${INTERNAL_TOKEN}"
    }
  }
}
```
