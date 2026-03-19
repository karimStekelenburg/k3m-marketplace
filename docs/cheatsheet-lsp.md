# .lsp.json / lspServers — Complete Schema Reference

LSP (Language Server Protocol) servers provide code intelligence to Claude Code — diagnostics, completions, go-to-definition, and more.

## Configuration Methods

### Method 1: Inline in plugin.json

```json
{
  "name": "my-lsp-plugin",
  "lspServers": {
    "<server-name>": { ...config }
  }
}
```

### Method 2: Inline in marketplace.json (strict: false)

```json
{
  "name": "my-lsp",
  "strict": false,
  "lspServers": { ...config }
}
```

### Method 3: .lsp.json at plugin root

```json
{
  "<server-name>": { ...config }
}
```

## Server Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | string | Yes | Executable to run |
| `args` | string[] | No | Command arguments (typically `["--stdio"]`) |
| `extensionToLanguage` | object | Yes | Maps file extensions to language IDs |
| `startupTimeout` | number | No | Startup timeout in ms (default varies by server) |

## extensionToLanguage

Maps file extensions to LSP language identifiers:

```json
"extensionToLanguage": {
  ".ts": "typescript",
  ".tsx": "typescriptreact",
  ".js": "javascript",
  ".jsx": "javascriptreact"
}
```

Common language IDs: `typescript`, `typescriptreact`, `javascript`, `javascriptreact`, `python`, `go`, `rust`, `c`, `cpp`, `java`, `kotlin`, `ruby`, `php`, `swift`, `csharp`, `lua`, `erb`

## Examples

### TypeScript/JavaScript

```json
{
  "typescript": {
    "command": "typescript-language-server",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".ts": "typescript",
      ".tsx": "typescriptreact",
      ".js": "javascript",
      ".jsx": "javascriptreact",
      ".mts": "typescript",
      ".cts": "typescript",
      ".mjs": "javascript",
      ".cjs": "javascript"
    }
  }
}
```

### Python (Pyright)

```json
{
  "pyright": {
    "command": "pyright-langserver",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".py": "python",
      ".pyi": "python"
    }
  }
}
```

### Go

```json
{
  "gopls": {
    "command": "gopls",
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

### Rust

```json
{
  "rust-analyzer": {
    "command": "rust-analyzer",
    "extensionToLanguage": {
      ".rs": "rust"
    }
  }
}
```

### Kotlin (with startup timeout)

```json
{
  "kotlin-lsp": {
    "command": "kotlin-lsp",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".kt": "kotlin",
      ".kts": "kotlin"
    },
    "startupTimeout": 120000
  }
}
```

## Gotchas

1. **LSP server must be installed** on the user's machine — document as a prerequisite
2. **`extensionToLanguage` is required** — Claude Code needs this to route files correctly
3. **Most servers use `--stdio`** — but some (like gopls) don't need it
4. **Use `startupTimeout`** for slow-starting servers (Java, Kotlin)
5. **LSP is typically defined with `strict: false`** in marketplace.json — the marketplace entry IS the plugin
6. **No `${CLAUDE_PLUGIN_ROOT}` needed** — commands are usually global binaries
