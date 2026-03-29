# K3M Marketplace -- Product Requirements Document

> **Core Purpose:** A self-maintaining plugin marketplace with infrastructure that minimizes plugin maintenance overhead so the developer can focus on actual work instead of fixing tooling.

## Problem Statement

After months of building Claude Code plugins ad-hoc -- skills, commands, agents -- the accumulated tooling is inconsistent, duplicative, and expensive to maintain. Instructions get copied across multiple plugins. Skills are overfit to specific contexts and break down outside them. When Claude Code ships new features or changes its plugin API, every affected plugin falls behind silently -- there is no mechanism to detect or correct this.

The practical cost: the developer sits down to do work, hits a broken or outdated skill, and spends the day fixing the skill instead of doing the task. Feedback about what's broken gets lost because there's nowhere to capture it without interrupting the current workflow. The tooling that was supposed to save time is consuming it.

The existing plugins were built without a unifying design philosophy. Rather than patching them, the goal is to rebuild the infrastructure from scratch with the benefit of hard-won experience, then build domain plugins on top of a solid foundation.

## Overview

The K3M Marketplace is a personal, curated plugin library located at `~/dev/k3m-marketplace`. It contains Claude Code plugins that can be installed, evaluated, improved, and maintained over time. Before adding more domain-specific plugins, the priority is establishing the core infrastructure: a meta-plugin that enforces organizational structure, an updated plugin-dev plugin that creates self-maintaining plugins, and a feedback system that captures issues without derailing active work.

The marketplace may later serve as a source for plugins shared within the developer's company, but v1 is for personal use.

## Goals

1. Eliminate duplicated instructions across plugins by enforcing single-responsibility organization and shared reference documents.
2. Reduce time spent on plugin maintenance by building self-update capabilities into every plugin the system creates.
3. Capture feedback about broken or suboptimal plugins in the moment, without interrupting the task at hand, so improvements can be batched and processed later.
4. Bring the plugin-dev plugin fully up to date with current Claude Code plugin capabilities, including evaluation infrastructure from Anthropic's skill-creator plugin.

## Non-Goals

- Building domain-specific plugins (those come after the infrastructure is solid).
- Supporting multiple users or access control (this is a personal marketplace).
- Automatic scheduled updates or cron-based triggers (manual commands first; scheduling can be layered on later).
- A web UI, dashboard, or visual management interface.
- Publishing to Anthropic's official plugin marketplace.

## Users and Personas

**Primary user:** A single developer (Karim) who builds and maintains Claude Code plugins for personal productivity. Technically proficient. Works across different types of projects -- sometimes prototyping quickly, sometimes building production systems. Expects plugins to be context-appropriate rather than one-size-fits-all. Does not want to spend time on plugin maintenance when doing actual work.

**Secondary (future):** Team members at the developer's company who may adopt well-tested plugins from this marketplace. This is not a v1 concern but informs design decisions -- plugins should be understandable and usable by others without the original author's context.

## Use Cases

### UC1: Enforcing marketplace organization

**Trigger:** The developer (or Claude, during a session) adds a new skill or instruction to a plugin. For example, conventional commit instructions get added to a general development plugin.

**Flow:** The meta-dev plugin detects that a version-control-specific instruction has been placed in the wrong plugin. It checks whether a version control plugin exists. If it does, and the instruction is already there, it rejects the duplication. If the plugin exists but lacks the instruction, it proposes moving it. If no appropriate plugin exists, it flags the gap.

**Outcome:** Instructions live in exactly one place. The marketplace stays organized as it grows.

### UC2: Creating a new plugin with self-update capabilities

**Trigger:** The developer wants a new plugin for a specific domain (e.g., testing, documentation, deployment).

**Flow:** The developer invokes the plugin-dev plugin's creation workflow. The plugin is scaffolded with standard structure, including: a reference docs directory that uses index-style pointers (URLs and descriptions of where to fetch current information) rather than copied content; a timestamp metadata field recording when reference docs were last verified; and a staleness-check command that compares timestamps against known release history.

**Outcome:** The new plugin is born with self-maintenance awareness. It knows how to check whether its reference material is current and how to update itself.

### UC3: Updating a plugin's reference documentation

**Trigger:** The developer runs a manual update command against a specific plugin (e.g., `/meta-dev:update plugin-dev`).

**Flow:** The system reads the plugin's reference doc index -- a manifest of what external documentation it depends on and where that documentation lives. It checks timestamps against Claude Code release notes to determine whether updates have occurred since the last verification. If updates are detected, it fetches the current documentation, compares it semantically against the plugin's existing reference material, identifies gaps or contradictions, and proposes updates. It handles the case where external documentation has moved (changed URLs, restructured sitemaps) by doing exploratory search rather than relying solely on stored URLs.

**Outcome:** The plugin's reference documentation is semantically current with the latest official documentation. The verification timestamp is updated.

### UC4: Capturing feedback during active work

**Trigger:** The developer is in the middle of a task. A skill misbehaves -- wrong output, irrelevant instructions for the current context, missing a feature. The developer does not want to stop and fix it now.

**Flow:** The developer invokes a lightweight feedback command (e.g., `/feedback "skill X is injecting performance benchmarking instructions during a quick prototype session"`). The system records the feedback tagged to the specific plugin and component (skill, command, agent, hook), with timestamp and context. This happens in the background -- the developer's current task is not interrupted.

**Outcome:** The feedback is stored in a structured location within the marketplace. The developer continues working. Later, a separate optimization pass can read all accumulated feedback and propose improvements.

### UC5: Processing accumulated feedback

**Trigger:** The developer decides to run an optimization pass, either on a specific plugin or across the marketplace.

**Flow:** The system reads all feedback entries for the target scope. It groups feedback by plugin and component, identifies patterns (e.g., "this skill is consistently too opinionated for lightweight projects"), and proposes concrete changes. Where Anthropic's skill-creator evaluation infrastructure applies (skills with description-based triggering), it can run A/B tests to compare the current version against a proposed improvement.

**Outcome:** Plugins improve over time based on real usage data rather than guesswork. Changes are proposed, not applied blindly -- the developer reviews and approves.

## Requirements

### Functional Requirements

**Meta-dev plugin**

FR1. Maintain a registry of all plugins in the marketplace, including their declared responsibility scope (what domain or concern each plugin owns).

FR2. When a new skill, command, or instruction is added to any plugin, validate that it belongs to that plugin's declared scope. If it belongs elsewhere, flag it and propose the correct location.

FR3. Detect duplicated instructions across plugins. When the same concern is addressed in multiple places, propose consolidation.

FR4. Manage a shared reference docs directory at the marketplace root. Enforce that cross-plugin instructions are stored there once and referenced via links, not copied into individual plugins.

FR5. Provide a plugin registration command that scaffolds a new plugin entry in the marketplace registry with its declared scope.

**Plugin-dev plugin**

FR6. Scaffold new plugins with standard structure: plugin.json, commands/, agents/, skills/, hooks/ directories, reference docs index, and staleness metadata.

FR7. Create plugins with reference documentation structured as an index (pointers to external sources with descriptions) rather than copied content.

FR8. Include a staleness-check capability in every scaffolded plugin: timestamp tracking, comparison against release notes or changelogs, and a command to trigger the check.

FR9. Support updating a plugin's reference documentation by: reading the reference index, detecting what has changed externally, fetching current documentation, comparing semantically, and proposing updates. Handle URL changes and sitemap restructuring through exploratory search.

FR10. Incorporate evaluation infrastructure aligned with Anthropic's skill-creator plugin: train/test splitting for skill description evaluation, iterative improvement, and reporting.

FR11. Stay current with Claude Code's plugin system capabilities. The plugin-dev plugin's own reference documentation about plugin structure, hooks, agents, commands, and skills must reflect the latest Claude Code platform features.

**Feedback and optimization system**

FR12. Provide a lightweight, fire-and-forget feedback capture command that records feedback tagged to a specific plugin and component, with timestamp and contextual information.

FR13. Store feedback in a structured, queryable format within the marketplace (e.g., per-plugin feedback directories with structured files).

FR14. Provide an optimization command that reads accumulated feedback, groups it by plugin/component, identifies patterns, and proposes concrete improvements.

FR15. Where applicable (skill descriptions, triggering behavior), integrate with evaluation infrastructure to A/B test proposed improvements against the current version.

### Non-Functional Requirements

NF1. **Low interruption.** Feedback capture and organizational validation must not block or significantly delay the developer's current task. Background execution where possible.

NF2. **Modularity.** Each plugin in the marketplace must be independently installable. No plugin should require another plugin to function, though plugins may benefit from each other's presence.

NF3. **Transparency.** All automated proposals (organizational corrections, reference doc updates, optimization suggestions) must be presented for review before being applied. No silent modifications.

## Constraints

**Technical platform:** Claude Code plugin system. All tooling must conform to the plugin structure (plugin.json manifest, commands/, agents/, skills/, hooks/ directories, optional .mcp.json). Reference: [Claude Code Plugins Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference).

**Known platform limitations:** Claude Code's plugin update mechanism has known issues -- marketplace clones don't auto-update, `CLAUDE_PLUGIN_ROOT` can resolve to stale cache directories, and `claude plugin update` may report false "up to date" status. The self-update capabilities in this marketplace must work around these limitations rather than depending on them being fixed upstream.

**Single developer.** No multi-user coordination, authentication, or permission systems needed in v1.

**Local-first.** The marketplace is a local git repository. No cloud services, databases, or external infrastructure required beyond what Claude Code already provides.

## Validation Roadmap

**Value proposition:** The developer can create, organize, and maintain plugins efficiently -- spending minutes on maintenance instead of hours -- because the infrastructure handles structural enforcement, staleness detection, and feedback-driven improvement.

**Current project state:** Partially built. A cloned plugin-dev plugin (from Anthropic's open-source repo) exists with partial updates. An in-progress meta-dev plugin concept exists. The marketplace repository is set up at `~/dev/k3m-marketplace`. What remains unproven: the structural enforcement logic, the self-update mechanism, and the feedback loop.

**Step 1 -- Prove the structural foundation.** Build the meta-dev plugin with plugin registration, scope validation, and duplication detection (FR1-FR5). Build or update the plugin-dev plugin with current Claude Code documentation and the self-update scaffolding pattern (FR6-FR9, FR11). This proves that the marketplace can enforce its own organization and that plugins can be created with self-maintenance baked in. The evaluation infrastructure (FR10) and feedback system (FR12-FR15) are excluded from this step.

**Step 2 -- Add the feedback loop.** Implement the feedback capture command and the optimization pass (FR12-FR15). Integrate evaluation infrastructure into plugin-dev (FR10). This completes the full circle: create plugins, maintain them, capture issues in the field, and improve them based on real usage.

**Deferred until value is proven:** Domain-specific plugins (testing, documentation, deployment, version control, etc.) are not built until the infrastructure that creates, organizes, and maintains them is working. Building domain plugins on broken infrastructure is how the current mess was created.

## Execution Plan

### Step 1: Audit the existing marketplace and plugin-dev plugin

**Goal:** Establish a clear baseline of what exists, what is current, and what is outdated. Every subsequent step depends on knowing the starting point accurately.

**Tasks:**
- Inventory all plugins, skills, commands, agents, and hooks currently in `~/dev/k3m-marketplace`.
- For each component in the plugin-dev plugin, compare against current Claude Code plugin documentation (https://docs.claude.com/en/docs/claude-code/plugins-reference) and the upstream Anthropic plugin-dev repo (https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev).
- Compare against Anthropic's skill-creator plugin (https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator) to identify evaluation infrastructure that should be merged in.
- Document findings: what is current, what is outdated, what is missing, what contradicts official docs.

**Done when:** A written audit report exists that maps every existing component to its status (current / outdated / missing / contradicting) with specific references to official documentation.

### Step 2: Define the marketplace organizational strategy

**Goal:** Establish the conventions and structures that the meta-dev plugin will enforce. This is a design step, not an implementation step -- the rules need to exist before the enforcer is built.

**Tasks:**
- Define the plugin scope declaration format (resolves Open Question 1). Start with natural language descriptions and a keyword list per plugin; evaluate whether Claude can match against these reliably.
- Define the shared reference docs directory structure at the marketplace root. Test that Claude Code resolves cross-plugin file references correctly (resolves Open Question 4).
- Define the reference doc index format: how each plugin declares its external documentation dependencies, URLs, descriptions, and last-verified timestamps.
- Define the feedback storage format (resolves Open Question 2). Prototype both per-plugin structured files and a central directory; pick one.
- Document all conventions in a marketplace-level architecture file.

**Done when:** A marketplace architecture document exists that specifies: plugin scope declaration format, shared reference docs structure, reference doc index format, feedback storage format, and naming/directory conventions. Cross-plugin file references have been tested and confirmed working.

### Step 3: Build the marketplace registry and meta-dev plugin skeleton

**Goal:** Implement the structural foundation -- the registry that knows what plugins exist and what they own, and the meta-dev plugin that can query it.

**Depends on:** Step 2 (conventions must be defined before they can be enforced).

**Tasks:**
- Create the plugin registry: a structured file (or directory) at the marketplace root listing all plugins with their declared scope, description, and component inventory.
- Scaffold the meta-dev plugin with standard plugin structure (plugin.json, commands/, skills/, agents/).
- Implement the plugin registration command (FR5): scaffolds a new plugin entry in the registry with its declared scope.
- Implement scope validation (FR2): when given a new skill or instruction and a target plugin, check whether it belongs to that plugin's declared scope.
- Implement duplication detection (FR3): scan across plugins for instructions addressing the same concern.

**Done when:** A new plugin can be registered via command. Adding a skill to the wrong plugin produces a clear warning with a proposed correction. Duplicated instructions across two plugins are detected and flagged.

### Step 4: Update the plugin-dev plugin to current Claude Code documentation

**Goal:** Bring plugin-dev fully up to date so it creates plugins that reflect the current platform capabilities. This is also the first real test of the staleness-detection workflow.

**Depends on:** Step 1 (audit identifies what is outdated).

**Tasks:**
- Update all reference documentation in plugin-dev to reflect current Claude Code plugin capabilities: hooks (all event types), agents (frontmatter fields), commands (YAML frontmatter, dynamic arguments), skills (progressive disclosure, evaluation).
- Convert reference docs to the index-and-fetch pattern defined in Step 2: replace copied content with pointers to official documentation URLs, with descriptions of what each source covers.
- Add staleness metadata: last-verified timestamp, list of external documentation dependencies.
- Merge evaluation infrastructure from Anthropic's skill-creator plugin (FR10): train/test splitting, iterative improvement, reporting.
- Verify the updated plugin-dev by using it to scaffold a test plugin and confirming the output matches current Claude Code conventions.

**Done when:** Plugin-dev's reference docs are semantically current with official documentation. Scaffolded plugins include reference doc indexes, staleness metadata, and evaluation infrastructure. A test plugin created by the updated plugin-dev passes validation against current Claude Code plugin conventions.

### Step 5: Implement the self-update mechanism

**Goal:** Build the staleness-check and update workflow so any plugin can verify and refresh its own reference documentation.

**Depends on:** Step 4 (plugin-dev must use the index pattern before the update mechanism can operate on it).

**Tasks:**
- Implement the staleness-check command (FR8): reads a plugin's reference doc index, compares last-verified timestamps against Claude Code release notes / changelogs, reports whether updates are likely needed.
- Implement the reference doc update workflow (FR9): fetches current documentation from indexed sources, compares semantically against existing reference material, identifies gaps or contradictions, proposes updates.
- Handle URL breakage: when a stored URL returns no useful content, fall back to exploratory search (search official docs for the topic described in the index entry).
- Test the full cycle: deliberately introduce a stale reference doc, run the staleness check, confirm it detects the issue, run the update, confirm it proposes the correct fix.

**Done when:** Running the staleness check against a plugin with outdated references correctly identifies the gaps. Running the update workflow proposes accurate corrections. URL breakage is handled gracefully via exploratory search fallback.

### Step 6: Implement the feedback capture system

**Goal:** Enable fire-and-forget feedback during active work sessions. This is the first half of the feedback loop.

**Depends on:** Step 3 (registry must exist so feedback can be tagged to the correct plugin/component).

**Tasks:**
- Implement the feedback capture command (FR12): accepts free-text feedback, auto-tags to plugin and component based on context (current session, active plugin, or explicit specification).
- Implement feedback storage (FR13): write feedback entries to the format defined in Step 2, with timestamp, plugin, component, and context fields.
- Ensure the command runs in the background and does not block or interrupt the developer's current task (NF1).
- Test by capturing feedback during an active work session and verifying it appears correctly in storage.

**Done when:** Feedback can be captured mid-task with a single command invocation. The command does not interrupt the active workflow. Feedback entries are correctly tagged and stored in the defined format.

### Step 7: Implement the optimization pass

**Goal:** Complete the feedback loop by building the system that reads accumulated feedback and proposes improvements.

**Depends on:** Step 6 (feedback must exist to process) and Step 4 (evaluation infrastructure must be in place).

**Tasks:**
- Implement the optimization command (FR14): reads all feedback for a target plugin or the entire marketplace, groups by component, identifies patterns, and proposes concrete changes.
- Integrate with evaluation infrastructure (FR15): for skill descriptions and triggering behavior, run A/B comparisons between the current version and proposed improvements using the train/test methodology from the skill-creator plugin.
- Ensure all proposals are presented for review before being applied (NF3).
- Test the full cycle: capture several feedback entries about a skill, run the optimization pass, verify it produces a sensible proposal that addresses the feedback patterns.

**Done when:** The optimization pass reads feedback, identifies patterns, and proposes specific, actionable changes. For skill descriptions, it can run evaluation comparisons. No changes are applied without explicit approval.

### Step 8: End-to-end validation

**Goal:** Verify the entire system works as a coherent whole by running through the complete lifecycle: create a plugin, use it, capture feedback, detect staleness, update, and optimize.

**Depends on:** All prior steps.

**Tasks:**
- Create a new test plugin using the updated plugin-dev. Verify it is registered correctly in the marketplace with proper scope declaration.
- Use the test plugin in a real work session. Capture feedback about its behavior.
- Simulate staleness by backdating the reference doc timestamps. Run the staleness check and update workflow.
- Run the optimization pass against the captured feedback. Review the proposals.
- Attempt to add a skill to the wrong plugin. Verify the meta-dev plugin catches it.
- Attempt to duplicate an instruction across plugins. Verify detection.
- Document any issues found and address them.

**Done when:** The full lifecycle works end-to-end without manual workarounds. All functional requirements (FR1-FR15) are demonstrably met. The developer can trust the infrastructure enough to start building domain plugins on top of it.

## Considered Alternatives

**Convention over enforcement.** Instead of a meta-dev plugin that actively validates placement, rely on documented conventions (a CONTRIBUTING.md or architecture decision record) and developer discipline. Rejected because the entire point is that Claude itself needs to follow the rules during development sessions. Passive documentation does not prevent Claude from putting conventional commit instructions in the wrong plugin. Active enforcement is the mechanism that makes the organizational strategy real.

**Separate feedback tool.** Build the feedback system as a standalone tool outside the marketplace rather than as part of the meta-dev plugin. Considered because feedback is conceptually different from structural enforcement. Rejected for v1 because feedback capture is marketplace infrastructure -- it needs to know the plugin registry to tag feedback correctly, and the optimization pass needs to know plugin structure to propose changes. Keeping it in the meta-dev plugin avoids unnecessary indirection.

**Copy-based reference documentation.** Store full copies of external documentation inside each plugin's reference docs rather than using an index-and-fetch pattern. Simpler to implement, and avoids the problem of broken external URLs. Rejected because it creates a new class of staleness -- copied docs go stale silently and there is no mechanism to detect the drift. The index pattern makes staleness detectable by design, even though it requires handling URL changes through exploratory search.

## Open Questions

1. **Scope declaration format.** How should plugins declare their responsibility scope for the meta-dev plugin to validate against? A simple keyword list? A natural language description? A structured taxonomy? The format affects how precisely the meta-dev plugin can detect misplacement. Needs experimentation.

2. **Feedback storage format.** What structure works best for feedback entries? Flat markdown files per plugin? A single structured file (YAML/JSON) per plugin? A central feedback directory? The format should make it easy to write (fire-and-forget) and easy to read (batch processing during optimization). Worth prototyping both approaches.

3. **Semantic comparison for reference doc updates.** How reliable is semantic comparison between a plugin's compressed reference material and the full external documentation? If the plugin's reference is a deliberately condensed version, detecting whether new information is missing (vs. intentionally omitted) is a judgment call. May need a human-in-the-loop step for the first few updates to calibrate.

4. **Cross-plugin reference doc linking.** Claude Code plugins can reference files outside their plugin directory. The shared reference docs pattern (root-level directory, linked from multiple plugins) needs testing to confirm it works reliably across different Claude Code session types and plugin loading mechanisms.

## Future Considerations

### Deferred enhancements

- **Scheduled staleness checks.** Periodic triggers (cron-style) that automatically check whether plugins need updating, rather than requiring a manual command. The manual command is v1; scheduling is a configuration layer on top.
- **Plugin health dashboard.** A summary view showing which plugins have pending feedback, which are stale, and which have been recently updated. Useful once the marketplace grows beyond a handful of plugins.
- **Plugin templates.** Pre-configured plugin scaffolds for common patterns (e.g., "reference-heavy plugin," "personal preferences plugin," "workflow automation plugin") that bake in the appropriate self-update strategy for each type.
- **Company distribution.** Packaging and sharing select plugins with team members. Requires documentation, onboarding guidance, and potentially stripping personal preferences from shared plugins.

### Parking Lot

No items were parked during this interview. The scope remained focused on infrastructure throughout.
