---
name: Scope Validation
description: This skill should be used when the user asks to "add a skill to a plugin", "move an instruction", "check if this belongs here", "validate placement", or when Claude is about to add a new skill, command, agent, hook, or instruction to any plugin in the K3M marketplace. Validates that content is being placed in the correct plugin based on declared scope ownership.
version: 0.1.0
---

# Scope Validation for K3M Marketplace

Validate that skills, commands, agents, hooks, and instructions are placed in the correct plugin based on the marketplace registry's scope declarations.

## When to activate

Activate this skill whenever:
- A new skill, command, agent, or hook is about to be added to a K3M marketplace plugin
- An existing instruction is being modified in a way that might change its scope
- The user explicitly asks whether something belongs in a particular plugin
- Content is being moved between plugins

## Process

### Step 1: Load the registry

Read `registry.yaml` from the marketplace root. The marketplace root is the parent of the `plugins/` directory. From any plugin, navigate up two levels from `${CLAUDE_PLUGIN_ROOT}`.

Parse all plugin entries with their `scope.keywords`, `scope.owns`, and `scope.does_not_own` fields.

### Step 2: Analyze the content being placed

Extract the key concepts from the content being added:
- What domain does it address? (e.g., hooks, skills, testing, version control)
- What specific responsibility does it implement? (e.g., "validate hook schema", "scaffold plugin structure")
- What keywords best describe it?

### Step 3: Keyword matching (fast filter)

Compare extracted keywords against each plugin's `scope.keywords`:
- Count keyword matches per plugin
- If one plugin matches significantly more keywords than others, it's the likely owner
- If multiple plugins match similarly, proceed to semantic matching

### Step 4: Semantic matching (judgment call)

Compare the content's purpose against each plugin's `scope.owns` entries:
- Does any plugin's `owns` list directly describe this content's purpose?
- Does any plugin's `does_not_own` list explicitly exclude this content?

The `does_not_own` field is authoritative — if plugin A says "does not own X (belongs to B)", the content belongs to B regardless of keyword overlap.

### Step 5: Report findings

**If the content is in the correct plugin:**
- Confirm the placement is valid
- Briefly explain why (which scope.owns entry it matches)

**If the content belongs in a different plugin:**
- Identify the correct plugin with reasoning
- Quote the relevant `scope.owns` and `scope.does_not_own` entries
- Propose moving the content
- If the target plugin exists, suggest the specific location
- If no appropriate plugin exists, flag the gap and suggest registering a new plugin

**If the placement is ambiguous:**
- Present the case for each candidate plugin
- Recommend the best fit with reasoning
- Suggest updating scope declarations if the ambiguity reveals a gap in the registry

### Step 6: Check for scope gaps

If the content doesn't clearly belong to any registered plugin:
- This indicates a gap in the marketplace's coverage
- Suggest registering a new plugin using `/marketplace-maintenance:register`
- Propose a scope declaration for the new plugin

## Key principle

Always err on the side of flagging potential misplacement. A false positive (flagging correct placement) is cheap — the user confirms and moves on. A false negative (missing a misplacement) leads to the organizational debt the marketplace is designed to prevent.

## Additional Resources

### Reference Files

For the complete registry format and scope declaration conventions:
- **`references/registry-format.md`** - Registry YAML format specification
