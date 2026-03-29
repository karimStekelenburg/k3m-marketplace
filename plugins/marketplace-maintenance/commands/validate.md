---
description: Run agnix validation on marketplace plugins in strict mode. Use before commits, after changes, or to audit plugin quality.
argument-hint: "[plugin-name|all]"
---

# Validate Marketplace Plugins

Run `agnix` in strict mode against marketplace plugins to catch configuration
errors, frontmatter issues, and best-practice violations.

## Input

$ARGUMENTS can be:
- A plugin name (e.g., `plugin-dev`) — validate that specific plugin
- `all` or empty — validate the entire marketplace

## Process

### Step 1: Run validation

```bash
# Single plugin
agnix --target claude-code --strict plugins/{plugin-name}

# Entire marketplace
agnix --target claude-code --strict .
```

### Step 2: Report results

Report the results grouped by severity:

1. **Errors** — must be fixed before committing
2. **Warnings** — should be fixed; treated as errors in strict mode
3. **Info** — informational; review but not blocking

For each finding, include the file path, line number, and the rule ID.

### Step 3: Suggest fixes

For fixable issues, suggest running:

```bash
# Preview fixes
agnix --target claude-code --strict --dry-run --show-fixes plugins/{plugin-name}

# Apply safe fixes only
agnix --target claude-code --strict --fix-safe plugins/{plugin-name}
```

Never apply `--fix-unsafe` without explicit user approval.
