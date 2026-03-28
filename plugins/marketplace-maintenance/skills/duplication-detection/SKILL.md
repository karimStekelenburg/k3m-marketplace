---
name: Duplication Detection
description: This skill should be used when the user asks to "check for duplicates", "find duplicate instructions", "audit marketplace for duplication", "consolidate instructions", or when a new skill or instruction is being added that might already exist elsewhere in the K3M marketplace. Detects and proposes consolidation of duplicated instructions across plugins.
version: 0.1.0
---

# Duplication Detection for K3M Marketplace

Detect duplicated instructions, skills, and content across plugins in the K3M marketplace and propose consolidation.

## When to activate

Activate this skill whenever:
- A new skill, command, or instruction is being added to any marketplace plugin
- The user explicitly asks to check for or audit duplication
- During an optimization pass that reviews marketplace health
- When the scope-validation skill identifies content that might overlap with another plugin

## Process

### Step 1: Determine scan scope

Based on the trigger:
- **New content being added:** Compare the new content against all existing plugins
- **Full audit:** Scan all plugins against each other
- **Targeted check:** Compare specific plugins or components

### Step 2: Load the registry

Read `registry.yaml` from the marketplace root to get the component inventory for each plugin. This tells us what skills, commands, agents, and hooks exist in each plugin.

### Step 3: Identify potential duplicates

For each component being checked, look for duplication at three levels:

**Level 1: Name-based (fast, high confidence)**
- Same or very similar skill/command names across different plugins
- Example: `hook-validation` in plugin A and `validate-hooks` in plugin B

**Level 2: Keyword-based (medium speed, medium confidence)**
- Components whose descriptions share significant keyword overlap
- Compare SKILL.md frontmatter descriptions across plugins
- Flag when >60% of keywords in one description appear in another

**Level 3: Semantic (slower, catches subtle duplication)**
- Read the SKILL.md body of flagged components
- Compare the actual instructions and workflows
- Identify when two skills teach the same procedure differently
- Detect when the same reference material is included in multiple plugins

### Step 4: Classify findings

For each potential duplicate, classify as:

**Exact duplicate:** Same content in multiple places. Consolidate immediately.

**Overlapping responsibility:** Different content addressing the same concern. One plugin should own it; the other should reference or defer to it.

**Complementary coverage:** Related but distinct content in different plugins. Not duplication — each plugin covers its own aspect. No action needed, but document the boundary.

**Shared foundation:** Content that multiple plugins legitimately need (e.g., Claude Code platform fundamentals). Should be in the `shared/` directory, not duplicated in each plugin.

### Step 5: Propose consolidation

For each finding that requires action:

1. Identify which plugin should own the content (using scope declarations from registry.yaml)
2. Propose specific changes:
   - For exact duplicates: Remove from the non-owning plugin, add reference/link to the owning plugin
   - For overlapping responsibility: Merge the best of both into the owning plugin, remove from the other
   - For shared foundation: Move to `shared/` directory, add symlinks from each plugin that needs it
3. Note any registry updates needed (e.g., updating `scope.owns` to clarify boundaries)

### Step 6: Present for review

All proposals are presented for review before being applied (NF3). Format:

```
## Duplication Finding: {topic}

**Found in:** plugin-a/skills/skill-x, plugin-b/skills/skill-y
**Classification:** {exact duplicate | overlapping responsibility | shared foundation}
**Recommended owner:** plugin-a (reason: scope.owns includes "{relevant statement}")

**Proposed action:**
1. Keep content in plugin-a/skills/skill-x
2. Remove duplicate from plugin-b/skills/skill-y
3. In plugin-b, add reference to plugin-a's version

**Registry updates needed:**
- None / Update scope.owns / Add does_not_own entry
```

## Duplication prevention

Beyond detecting existing duplication, this skill helps prevent new duplication by:

1. **Pre-addition check:** Before any new content is added, scan existing plugins for similar content
2. **Shared reference pattern:** When content is needed by multiple plugins, recommend the shared/ directory with symlinks rather than copying
3. **Clear ownership:** Ensure registry.yaml scope declarations don't have overlapping `owns` statements

## Additional Resources

### Reference Files

For the registry format used in duplication detection:
- **`references/consolidation-patterns.md`** - Common consolidation patterns and examples
