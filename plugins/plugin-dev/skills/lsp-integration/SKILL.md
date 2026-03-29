---
name: lsp-integration
description: Use when user wants to This skill should be used when the user asks to "add LSP server", "configure language server", "add code intelligence", "set up go to definition", "configure find references", "add diagnostics", "language server protocol in plugin", or needs guidance on .lsp.json configuration, language server setup, or LSP integration in Claude Code plugins.
version: 0.1.0
---

# LSP Integration for Claude Code Plugins

## Overview

Plugins can provide Language Server Protocol (LSP) servers to give Claude real-time code intelligence: instant diagnostics, go to definition, find references, hover information, and type awareness.

## Configuration

### .lsp.json (at plugin root)

```json
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

### Inline in plugin.json

```json
{
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
}
```

## Required Fields

| Field | Description |
|-------|-------------|
| `command` | LSP binary to execute (must be in PATH) |
| `extensionToLanguage` | Maps file extensions to language identifiers |

## Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
| `args` | Command-line arguments | `[]` |
| `transport` | Communication: `stdio` or `socket` | `stdio` |
| `env` | Environment variables | `{}` |
| `initializationOptions` | Options for server initialization | `{}` |
| `settings` | Settings via `workspace/didChangeConfiguration` | `{}` |
| `workspaceFolder` | Workspace folder path | project root |
| `startupTimeout` | Max startup wait (ms) | default |
| `shutdownTimeout` | Max shutdown wait (ms) | default |
| `restartOnCrash` | Auto-restart on crash | `false` |
| `maxRestarts` | Max restart attempts | default |

## Important: Binary installation

LSP plugins configure how Claude Code connects to a language server, but do NOT include the server binary. Users must install separately:

| Language | Server | Install |
|----------|--------|---------|
| Python | Pyright | `pip install pyright` or `npm install -g pyright` |
| TypeScript | typescript-language-server | `npm install -g typescript-language-server typescript` |
| Rust | rust-analyzer | See rust-analyzer docs |
| Go | gopls | `go install golang.org/x/tools/gopls@latest` |

## Best practices

- Document the required binary installation in the plugin README
- Use `restartOnCrash: true` for reliability in long sessions
- Set reasonable `startupTimeout` for large workspaces
- Test with `claude --debug` to see LSP initialization details
- Check `/plugin` Errors tab for "Executable not found in $PATH" messages
