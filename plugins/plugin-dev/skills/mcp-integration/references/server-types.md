# MCP Server Types: Deep Dive

Complete reference for all MCP server types supported in Claude Code plugins.

## stdio (Standard Input/Output)

### Overview

Execute local MCP servers as child processes with communication via stdin/stdout. Best choice for local tools, custom servers, and NPM packages.

### Configuration

**Basic:**
```json
{
  "my-server": {
    "command": "npx",
    "args": ["-y", "my-mcp-server"]
  }
}
```

**With environment:**
```json
{
  "my-server": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/custom-server",
    "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
    "env": {
      "API_KEY": "${MY_API_KEY}",
      "LOG_LEVEL": "debug",
      "DATABASE_URL": "${DB_URL}"
    }
  }
}
```

### Process Lifecycle

1. **Startup**: Claude Code spawns process with `command` and `args`
2. **Communication**: JSON-RPC messages via stdin/stdout
3. **Lifecycle**: Process runs for entire Claude Code session
4. **Shutdown**: Process terminated when Claude Code exits

### Use Cases

**NPM Packages:**
```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
  }
}
```

**Custom Scripts:**
```json
{
  "custom": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/my-server.js",
    "args": ["--verbose"]
  }
}
```

**Python Servers:**
```json
{
  "python-server": {
    "command": "python",
    "args": ["-m", "my_mcp_server"],
    "env": {
      "PYTHONUNBUFFERED": "1"
    }
  }
}
```

### Best Practices

1. **Use absolute paths or ${CLAUDE_PLUGIN_ROOT}**
2. **Set PYTHONUNBUFFERED for Python servers**
3. **Pass configuration via args or env, not stdin**
4. **Handle server crashes gracefully**
5. **Log to stderr, not stdout (stdout is for MCP protocol)**

### Troubleshooting

**Server won't start:**
- Check command exists and is executable
- Verify file paths are correct
- Check permissions
- Review `claude --debug` logs

**Communication fails:**
- Ensure server uses stdin/stdout correctly
- Check for stray print/console.log statements
- Verify JSON-RPC format

## SSE (Server-Sent Events) — DEPRECATED

> **Deprecated:** SSE transport is deprecated. Use the `http` type for all new remote MCP servers. SSE support may be removed in a future release.

### Overview

Connect to hosted MCP servers via HTTP with server-sent events for streaming. Previously used for cloud services and OAuth authentication. New integrations should use `http` instead.

### Configuration

**Basic:**
```json
{
  "hosted-service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse"
  }
}
```

**With headers:**
```json
{
  "service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse",
    "headers": {
      "X-API-Version": "v1",
      "X-Client-ID": "${CLIENT_ID}"
    }
  }
}
```

### Connection Lifecycle

1. **Initialization**: HTTP connection established to URL
2. **Handshake**: MCP protocol negotiation
3. **Streaming**: Server sends events via SSE
4. **Requests**: Client sends HTTP POST for tool calls
5. **Reconnection**: Automatic reconnection on disconnect

### Authentication

**OAuth (Automatic):**
```json
{
  "asana": {
    "type": "sse",
    "url": "https://mcp.asana.com/sse"
  }
}
```

Claude Code handles OAuth flow:
1. User prompted to authenticate on first use
2. Opens browser for OAuth flow
3. Tokens stored securely
4. Automatic token refresh

**Custom Headers:**
```json
{
  "service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}"
    }
  }
}
```

### Use Cases

**Official Services:**
- Asana: `https://mcp.asana.com/sse`
- GitHub: `https://mcp.github.com/sse`
- Other hosted MCP servers

**Custom Hosted Servers:**
Deploy your own MCP server and expose via HTTPS + SSE.

### Best Practices

1. **Always use HTTPS, never HTTP**
2. **Let OAuth handle authentication when available**
3. **Use environment variables for tokens**
4. **Handle connection failures gracefully**
5. **Document OAuth scopes required**

### Troubleshooting

**Connection refused:**
- Check URL is correct and accessible
- Verify HTTPS certificate is valid
- Check network connectivity
- Review firewall settings

**OAuth fails:**
- Clear cached tokens
- Check OAuth scopes
- Verify redirect URLs
- Re-authenticate

## HTTP (REST API)

### Overview

Connect to RESTful MCP servers via standard HTTP requests. Best for token-based auth and stateless interactions.

### Configuration

**Basic:**
```json
{
  "api": {
    "type": "http",
    "url": "https://api.example.com/mcp"
  }
}
```

**With authentication:**
```json
{
  "api": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}",
      "Content-Type": "application/json",
      "X-API-Version": "2024-01-01"
    }
  }
}
```

### Request/Response Flow

1. **Tool Discovery**: GET to discover available tools
2. **Tool Invocation**: POST with tool name and parameters
3. **Response**: JSON response with results or errors
4. **Stateless**: Each request independent

### Authentication

**Token-Based:**
```json
{
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  }
}
```

**API Key:**
```json
{
  "headers": {
    "X-API-Key": "${API_KEY}"
  }
}
```

**Custom Auth:**
```json
{
  "headers": {
    "X-Auth-Token": "${AUTH_TOKEN}",
    "X-User-ID": "${USER_ID}"
  }
}
```

### Use Cases

- REST API backends
- Internal services
- Microservices
- Serverless functions

### Best Practices

1. **Use HTTPS for all connections**
2. **Store tokens in environment variables**
3. **Implement retry logic for transient failures**
4. **Handle rate limiting**
5. **Set appropriate timeouts**

### Troubleshooting

**HTTP errors:**
- 401: Check authentication headers
- 403: Verify permissions
- 429: Implement rate limiting
- 500: Check server logs

**Timeout issues:**
- Increase timeout if needed
- Check server performance
- Optimize tool implementations

## Comparison Matrix

| Feature | stdio | SSE (deprecated) | HTTP |
|---------|-------|------------------|------|
| **Transport** | Process | HTTP/SSE | HTTP |
| **Direction** | Bidirectional | Server→Client | Request/Response |
| **State** | Stateful | Stateful | Stateless |
| **Auth** | Env vars | OAuth/Headers | Headers |
| **Use Case** | Local tools | Legacy cloud services | Remote services, REST APIs |
| **Latency** | Lowest | Medium | Medium |
| **Setup** | Easy | Medium | Easy |
| **Reconnect** | Process respawn | Automatic | N/A |

## Choosing the Right Type

**Use stdio when:**
- Running local tools or custom servers
- Need lowest latency
- Working with file systems or local databases
- Distributing server with plugin

**Use HTTP when (recommended for all remote servers):**
- Connecting to hosted or cloud services
- Integrating with REST APIs
- Using token-based or header auth
- Simple request/response pattern
- Building any new remote MCP integration

**Avoid SSE for new integrations** — SSE is deprecated. Migrate existing SSE servers to HTTP transport.

## Migration Between Types

### From stdio to SSE

**Before (stdio):**
```json
{
  "local-server": {
    "command": "node",
    "args": ["server.js"]
  }
}
```

**After (SSE - deploy server):**
```json
{
  "hosted-server": {
    "type": "sse",
    "url": "https://mcp.example.com/sse"
  }
}
```

### From SSE to HTTP

**Before (SSE — deprecated):**
```json
{
  "hosted-server": {
    "type": "sse",
    "url": "https://mcp.example.com/sse"
  }
}
```

**After (HTTP — recommended):**
```json
{
  "hosted-server": {
    "type": "http",
    "url": "https://mcp.example.com/mcp"
  }
}
```

Benefits: Uses the current recommended transport, avoids deprecated API surface.

## Advanced Configuration

### Multiple Servers

Combine different types:

```json
{
  "local-db": {
    "command": "npx",
    "args": ["-y", "mcp-server-sqlite", "./data.db"]
  },
  "cloud-api": {
    "type": "sse",
    "url": "https://mcp.example.com/sse"
  },
  "internal-service": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}"
    }
  }
}
```

### Conditional Configuration

Use environment variables to switch servers:

```json
{
  "api": {
    "type": "http",
    "url": "${API_URL}",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}"
    }
  }
}
```

Set different values for dev/prod:
- Dev: `API_URL=http://localhost:8080/mcp`
- Prod: `API_URL=https://api.production.com/mcp`

## Security Considerations

### Stdio Security

- Validate command paths
- Don't execute user-provided commands
- Limit environment variable access
- Restrict file system access

### Network Security

- Always use HTTPS
- Validate SSL certificates
- Don't skip certificate verification
- Use secure token storage

### Token Management

- Never hardcode tokens
- Use environment variables
- Rotate tokens regularly
- Implement token refresh
- Document scopes required

## Conclusion

Choose the MCP server type based on your use case:
- **stdio** for local, custom, or NPM-packaged servers
- **HTTP** for all remote servers and cloud services (recommended)
- **SSE** only for legacy compatibility — deprecated, migrate to HTTP

Test thoroughly and handle errors gracefully for robust MCP integration.
