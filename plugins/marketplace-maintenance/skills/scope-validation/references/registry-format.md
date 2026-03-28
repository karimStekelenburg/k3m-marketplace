# Registry Format Reference

The K3M marketplace registry (`registry.yaml`) is the authoritative source for plugin scope declarations.

## Complete entry format

```yaml
plugins:
  plugin-name:
    description: >
      One-paragraph description of the plugin's purpose and domain.
    version: "0.1.0"
    scope:
      keywords:
        - keyword1
        - keyword2
      owns:
        - "Responsibility statement 1"
        - "Responsibility statement 2"
      does_not_own:
        - "Thing this plugin does NOT own (belongs to other-plugin)"
    components:
      skills:
        - skill-name-1
        - skill-name-2
      commands:
        - command-name-1
      agents:
        - agent-name-1
```

## Field semantics

### scope.keywords
Fast-match terms for the plugin's domain. Used for initial filtering.
Keep to 8-15 keywords per plugin. Prefer specific terms over generic ones.

### scope.owns
Natural language statements of what this plugin is responsible for.
Each statement should be specific enough that a reasonable person (or Claude) can
determine whether a given piece of content falls within it.

Good: "Hook development patterns for all 22 event types"
Bad: "Hook stuff"

### scope.does_not_own
Explicit exclusions with redirect. Format: "Thing (belongs to other-plugin)"
This field is the strongest signal in scope validation — it overrides keyword overlap.

Good: "Marketplace organization and registry (belongs to marketplace-maintenance)"
Bad: "Other things"

### components
Inventory of what the plugin currently contains. Updated as skills, commands,
agents, and hooks are added or removed. Used for duplication detection.

## Validation rules

1. Every plugin in the marketplace MUST have a registry entry
2. Every `scope.owns` statement should be unique across plugins
3. Every `scope.does_not_own` should reference a valid plugin
4. Keywords should not have >50% overlap between plugins (warning threshold)
5. Component names must match actual files in the plugin directory
