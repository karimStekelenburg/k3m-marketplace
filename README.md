# k3m-marketplace

A curated collection of Claude Code plugins

## Getting Started

### Install this marketplace

```bash
claude plugin marketplace add /path/to/k3m-marketplace
```

### Browse available plugins

```bash
claude plugin search
```

### Enable a plugin

```bash
claude plugin enable <plugin-name>
```

## Adding Plugins

1. Create a new plugin directory under `plugins/`:
   ```bash
   copier copy /path/to/dotclaude/templates/plugin plugins/
   ```

2. Register it in `.claude-plugin/marketplace.json`

3. Validate:
   ```bash
   claude plugin validate plugins/<plugin-name>
   ```

## Documentation

See `docs/` for complete cheatsheets on every plugin component type.

## Maintainer

k3m.sh <me@k3m.sh>
