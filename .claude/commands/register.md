---
description: Register a new plugin in the K3M marketplace registry. Use when adding a new plugin to the marketplace or updating an existing plugin's scope declaration.
---

# Register Plugin

Register a new plugin in the K3M marketplace registry, or update an existing plugin's registration.

## What this command does

1. Reads the current marketplace registry at `${CLAUDE_PLUGIN_ROOT}/../../registry.yaml`
2. Prompts for the plugin details if not provided via $ARGUMENTS
3. Adds or updates the plugin entry in the registry
4. Scaffolds the plugin directory structure if it doesn't exist
5. Updates `marketplace.json` to include the new plugin

## Input

$ARGUMENTS should be the plugin name in kebab-case. If no arguments are provided, prompt the user for the plugin name.

## Process

### Step 1: Determine marketplace root

The marketplace root is the parent directory of the `plugins/` directory that contains this plugin. Resolve it by navigating from `${CLAUDE_PLUGIN_ROOT}` up two levels.

Read the registry file at `{marketplace_root}/registry.yaml`.

### Step 2: Gather plugin information

If the plugin already exists in the registry, show its current registration and ask what to update.

If the plugin is new, gather:
- **name**: kebab-case identifier (from $ARGUMENTS or ask)
- **description**: One-paragraph description of what the plugin does
- **scope.keywords**: List of keywords that describe the plugin's domain
- **scope.owns**: List of responsibilities this plugin owns (natural language)
- **scope.does_not_own**: List of things explicitly outside this plugin's scope, with notes about which plugin owns them instead

### Step 3: Validate against existing plugins

Before registering, check for conflicts:
- Does any existing plugin's `scope.owns` overlap with the new plugin's `scope.owns`?
- Do the keywords overlap significantly with an existing plugin?
- If conflicts are found, present them and ask the user to resolve before proceeding.

### Step 4: Write to registry

Add the new plugin entry to `registry.yaml` following the existing format. Include all fields: description, version (start at "0.1.0"), scope (keywords, owns, does_not_own), and components (initially empty lists).

### Step 5: Scaffold directory structure

If the plugin directory doesn't exist at `{marketplace_root}/plugins/{plugin-name}/`, create:

```
plugins/{plugin-name}/
├── .claude-plugin/
│   └── plugin.json
├── commands/
├── skills/
├── agents/
└── hooks/
```

Create a minimal `plugin.json` with name, description, version, and author fields.

### Step 6: Update marketplace.json

Add the plugin to the `plugins` array in `{marketplace_root}/.claude-plugin/marketplace.json` with:
- name
- source: `./plugins/{plugin-name}`
- description
- version: "0.1.0"
- category (ask if not obvious)
- tags (derived from scope keywords)

### Step 7: Confirm

Report what was created/updated:
- Registry entry
- Directory structure (if new)
- marketplace.json entry (if new)

Remind the user to create skills, commands, and agents for the plugin, and to update the registry's `components` section as they add them.
