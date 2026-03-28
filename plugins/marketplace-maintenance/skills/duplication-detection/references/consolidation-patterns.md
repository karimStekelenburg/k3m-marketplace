# Consolidation Patterns

Common patterns for resolving duplication in the K3M marketplace.

## Pattern 1: Move to shared references

**When:** Multiple plugins need the same foundational knowledge (e.g., Claude Code plugin structure basics, hook event reference).

**Action:**
1. Create a document in `shared/claude-code-platform/docs/`
2. Add a symlink from each plugin that needs it: `ln -s ../../../shared shared`
3. Reference the shared doc from each plugin's SKILL.md
4. Remove the duplicated content from individual plugins

**Example:**
Both plugin-dev and marketplace-maintenance reference the complete list of 22 hook events.
→ Move hook event reference to `shared/claude-code-platform/docs/hooks-reference.md`
→ Both plugins symlink to shared/ and reference the doc

## Pattern 2: Single owner with cross-reference

**When:** One plugin should own the content; another plugin references it occasionally.

**Action:**
1. Keep the content in the owning plugin (per registry.yaml scope)
2. In the non-owning plugin, add a brief note: "For X, see plugin-Y's skill-Z"
3. Update registry.yaml `does_not_own` if not already explicit

**Example:**
plugin-dev has hook development patterns. marketplace-maintenance needs to validate hooks.
→ plugin-dev owns hook development guidance
→ marketplace-maintenance references plugin-dev's guidance when validating hooks

## Pattern 3: Split by concern

**When:** Two plugins have overlapping content, but each covers a different aspect.

**Action:**
1. Identify the boundary between the two aspects
2. Split the content along that boundary
3. Update each plugin's SKILL.md to cover only its aspect
4. Add cross-references between the two
5. Update registry.yaml `scope.owns` to reflect the split

**Example:**
marketplace-maintenance and plugin-dev both discuss plugin.json format.
→ plugin-dev owns "how to create a valid plugin.json" (authoring guidance)
→ marketplace-maintenance owns "how to validate plugin.json against the registry" (enforcement)
→ Both reference the shared plugins-reference.md for the canonical schema

## Pattern 4: Consolidate into one

**When:** Two skills/commands do essentially the same thing with minor variations.

**Action:**
1. Determine which version is better (more complete, better structured)
2. Merge any unique value from the other version
3. Delete the inferior version
4. Update registry.yaml components list
5. Ensure no broken references

## Anti-patterns

**Don't consolidate complementary coverage.** If plugin-dev has "how to write hooks" and marketplace-maintenance has "how to validate marketplace organization," these are related but distinct. Don't force them together.

**Don't over-centralize into shared/.** Only put content in shared/ if it's truly foundational and needed by 2+ plugins. Plugin-specific guidance stays in the plugin.

**Don't remove content without checking references.** Before removing duplicate content, grep for references to it across all plugins.
