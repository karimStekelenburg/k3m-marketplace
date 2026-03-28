# K3M Marketplace — Architecture & Conventions

**Status:** Definitive reference for all marketplace conventions
**Date:** 2026-03-27

---

## 1. Marketplace Directory Structure

```
~/dev/k3m-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog
├── plugins/
│   ├── meta-dev/                 # Marketplace infrastructure plugin
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── commands/
│   │   ├── skills/
│   │   ├── agents/
│   │   └── hooks/
│   └── plugin-dev/               # Plugin development toolkit
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── commands/
│       ├── skills/
│       ├── agents/
│       └── hooks/
├── shared/                       # Shared reference material (symlinked into plugins)
│   └── claude-code-platform/     # Official Claude Code platform documentation
│       ├── index.yaml            # Reference doc index (URLs + descriptions + timestamps)
│       └── docs/                 # Fetched/condensed reference material
│           ├── plugins-reference.md
│           ├── hooks-reference.md
│           ├── skills-reference.md
│           ├── agents-reference.md
│           └── marketplace-reference.md
├── registry.yaml                 # Plugin registry (what exists, what it owns)
├── feedback/                     # Centralized feedback storage
│   ├── meta-dev/                 # Feedback entries for meta-dev plugin
│   └── plugin-dev/               # Feedback entries for plugin-dev plugin
├── architecture.md               # This file
├── audit-report.md               # Step 1 audit findings
└── k3m-marketplace-prd.md        # Product Requirements Document
```

### Why this structure

Plugins live under `plugins/` as required by marketplace conventions. The `shared/` directory holds cross-plugin reference material — each plugin symlinks to it so the content is available both in local development (`--plugin-dir`) and after marketplace installation (symlinks are followed during cache copy). The `feedback/` directory is centralized at the marketplace root because feedback processing spans plugins.

---

## 2. Plugin Scope Declaration Format

> Resolves Open Question 1 from the PRD.

Each plugin declares its responsibility scope in both its `plugin.json` (for Claude Code) and the marketplace `registry.yaml` (for the meta-dev plugin to validate against).

### Format in registry.yaml

```yaml
plugins:
  meta-dev:
    description: >
      Marketplace infrastructure: plugin registration, scope validation,
      duplication detection, shared reference doc management, feedback
      capture and optimization.
    scope:
      keywords:
        - marketplace
        - registry
        - scope-validation
        - duplication-detection
        - feedback
        - optimization
        - shared-references
        - staleness
      owns:
        - "Plugin registration and deregistration"
        - "Cross-plugin instruction placement validation"
        - "Duplication detection across plugins"
        - "Shared reference doc management at marketplace root"
        - "Feedback capture and storage"
        - "Feedback-driven optimization passes"
        - "Staleness detection and reference doc updates"
      does_not_own:
        - "Plugin creation scaffolding (belongs to plugin-dev)"
        - "Domain-specific skill content"
    components:
      skills: [scope-validation, duplication-detection, feedback-capture, optimization-pass, staleness-check, reference-update]
      commands: [register, validate, feedback, optimize, check-staleness, update-refs]
      agents: [scope-reviewer]

  plugin-dev:
    description: >
      Plugin development toolkit: scaffolding new plugins, skill/command/agent/hook
      development guidance, MCP integration, evaluation infrastructure.
    scope:
      keywords:
        - plugin-creation
        - scaffolding
        - skill-development
        - command-development
        - agent-development
        - hook-development
        - mcp-integration
        - evaluation
        - testing
      owns:
        - "Creating new plugin scaffolds"
        - "Skill authoring guidance and evaluation"
        - "Command development patterns"
        - "Agent development patterns"
        - "Hook development patterns"
        - "MCP server integration guidance"
        - "LSP server integration guidance"
        - "Plugin validation and testing"
      does_not_own:
        - "Marketplace organization (belongs to meta-dev)"
        - "Feedback processing (belongs to meta-dev)"
        - "Domain-specific plugin content"
    components:
      skills: [plugin-structure, skill-development, command-development, agent-development, hook-development, mcp-integration, lsp-integration, plugin-settings]
      commands: [create-plugin]
      agents: [agent-creator, skill-reviewer, plugin-validator]
```

### How scope validation works

The meta-dev plugin uses a two-pass approach:

1. **Keyword match (fast filter):** When a new instruction or skill is proposed for a plugin, extract keywords from the content and compare against all plugins' `scope.keywords`. If the best keyword match is a different plugin, flag it.

2. **Semantic match (judgment call):** If keyword matching is ambiguous, use the `scope.owns` and `scope.does_not_own` natural language descriptions to make a judgment. This is where Claude's reasoning handles edge cases that keyword lists can't.

The `does_not_own` field is particularly important — it creates explicit boundaries that prevent scope creep. When plugin A explicitly says "does not own X (belongs to B)", that's an unambiguous signal.

---

## 3. Shared Reference Docs Structure

> Resolves Open Question 4 from the PRD. Cross-plugin file references tested: symlinks work.

### Directory layout

```
shared/
└── claude-code-platform/
    ├── index.yaml                # Reference doc index
    └── docs/                     # Fetched/condensed reference docs
        ├── plugins-reference.md
        ├── hooks-reference.md
        ├── skills-reference.md
        ├── agents-reference.md
        ├── marketplace-reference.md
        └── settings-reference.md
```

### Cross-plugin access pattern

Each plugin that needs shared reference material creates a symlink:

```bash
# Inside plugin-dev directory:
ln -s ../../../shared shared

# Results in:
plugins/plugin-dev/shared -> ../../../shared
```

**Why symlinks work:**
- During local development (`claude --plugin-dir ./plugins/plugin-dev`), the symlink resolves directly.
- When installed via marketplace, Claude Code follows symlinks during cache copy. The shared content is physically present in each plugin's cache.
- Trade-off: shared content is duplicated in cache. Acceptable for a personal marketplace.

### Adding new shared reference topics

To add a new shared reference topic (e.g., for a new Claude Code feature area):

1. Create the directory under `shared/` with an `index.yaml` and `docs/` subdirectory
2. Add the symlink in each plugin that needs access
3. Register the topic in the marketplace-level index

---

## 4. Reference Doc Index Format

Each shared reference topic and each plugin has a reference doc index that declares external documentation dependencies.

### Format: index.yaml

```yaml
# shared/claude-code-platform/index.yaml
name: Claude Code Platform Documentation
last_verified: "2026-03-27T00:00:00Z"

sources:
  - id: plugins-reference
    url: "https://code.claude.com/docs/en/plugins-reference"
    description: >
      Complete technical reference for plugin system: manifest schema,
      component specs (skills, agents, hooks, MCP, LSP), directory
      structure, CLI commands, debugging tools.
    local_doc: docs/plugins-reference.md
    last_fetched: "2026-03-27T00:00:00Z"
    coverage_notes: >
      Condensed from official docs. Covers all 22 hook events, LSP servers,
      userConfig, channels, ${CLAUDE_PLUGIN_DATA}, output styles.

  - id: hooks-reference
    url: "https://code.claude.com/docs/en/hooks"
    description: >
      Detailed hooks documentation: all event types, hook types (command,
      http, prompt, agent), input/output formats, matchers, environment
      variables.
    local_doc: docs/hooks-reference.md
    last_fetched: "2026-03-27T00:00:00Z"

  - id: skills-reference
    url: "https://code.claude.com/docs/en/skills"
    description: >
      Skills authoring: SKILL.md format, frontmatter fields, progressive
      disclosure, auto-discovery, $ARGUMENTS, disable-model-invocation.
    local_doc: docs/skills-reference.md
    last_fetched: "2026-03-27T00:00:00Z"

  - id: agents-reference
    url: "https://code.claude.com/docs/en/sub-agents"
    description: >
      Agent configuration: frontmatter fields (model, effort, maxTurns,
      tools, disallowedTools, skills, memory, background, isolation),
      integration points.
    local_doc: docs/agents-reference.md
    last_fetched: "2026-03-27T00:00:00Z"

  - id: marketplace-reference
    url: "https://code.claude.com/docs/en/plugin-marketplaces"
    description: >
      Marketplace creation and distribution: marketplace.json schema,
      plugin sources (github, url, git-subdir, npm, relative path),
      version management, hosting, strict mode.
    local_doc: docs/marketplace-reference.md
    last_fetched: "2026-03-27T00:00:00Z"

  - id: settings-reference
    url: "https://code.claude.com/docs/en/settings"
    description: >
      Settings and configuration: scopes, settings files, plugin settings,
      extraKnownMarketplaces, strictKnownMarketplaces.
    local_doc: docs/settings-reference.md
    last_fetched: "2026-03-27T00:00:00Z"

changelog_sources:
  - url: "https://code.claude.com/docs/en/changelog"
    description: "Claude Code changelog — used for staleness detection"
  - url: "https://code.claude.com/docs/llms.txt"
    description: "Documentation index — used for discovering moved/new pages"
```

### How staleness detection works

1. **Compare timestamps:** Check `last_fetched` against the changelog. If the changelog has entries newer than `last_fetched` that mention relevant topics (hooks, plugins, skills, etc.), the reference is potentially stale.

2. **Fetch and compare:** For sources flagged as potentially stale, fetch the current URL content and compare semantically against `local_doc`. Identify additions, removals, and contradictions.

3. **Handle URL breakage:** If a stored URL returns no useful content (404, redirect to unrelated page), fall back to searching `llms.txt` (the documentation index) for the topic described in the `description` field.

4. **Update proposal:** Present a diff of proposed changes to the local_doc file. Never auto-apply.

---

## 5. Feedback Storage Format

> Resolves Open Question 2 from the PRD.

### Decision: Centralized directory with per-plugin subdirectories, one YAML file per entry

```
feedback/
├── meta-dev/
│   ├── 2026-03-27T14-30-00_scope-validation.yaml
│   └── 2026-03-28T09-15-00_duplication-detection.yaml
└── plugin-dev/
    ├── 2026-03-27T16-45-00_hook-development.yaml
    └── 2026-03-29T11-00-00_skill-development.yaml
```

### Entry format

```yaml
# feedback/plugin-dev/2026-03-27T16-45-00_hook-development.yaml
plugin: plugin-dev
component:
  type: skill               # skill | command | agent | hook | general
  name: hook-development
timestamp: "2026-03-27T16:45:00Z"
context:
  task: "Building a custom linting hook for a Python project"
  session_type: development  # development | prototyping | production | maintenance
severity: minor              # minor | moderate | major | critical
feedback: >
  The hook-development skill only lists 9 hook events but Claude Code now
  supports 22. When I asked to create a FileChanged hook, the skill had
  no guidance and Claude fell back to guessing the format.
tags:
  - outdated-reference
  - missing-event-type
  - FileChanged
status: open                 # open | addressed | wont-fix
resolution: null             # Filled in by optimization pass
```

### Why this format

- **One file per entry:** Fire-and-forget — writing a new entry never requires reading or modifying existing entries. No merge conflicts.
- **YAML over JSON:** More readable for human review, supports multi-line strings cleanly.
- **Centralized over per-plugin:** The optimization pass needs to read feedback across plugins to identify patterns. A central location makes this a single directory scan rather than walking every plugin.
- **Timestamp in filename:** Natural chronological ordering, unique keys, easy to sort.
- **Tags field:** Enables pattern detection during optimization. Tags like `outdated-reference`, `wrong-context`, `missing-feature` can be aggregated.

### Capturing feedback

The feedback command (`/meta-dev:feedback`) accepts free text and auto-extracts:
- **Plugin:** From context (which plugin/skill is active) or explicit mention
- **Component:** From context or explicit mention
- **Timestamp:** Auto-generated
- **Tags:** Auto-suggested based on content analysis, user can override
- **Severity:** Auto-suggested, user can override
- **Context:** Auto-captured from session state (current task description if available)

---

## 6. Naming and Directory Conventions

### Plugin naming
- kebab-case: `meta-dev`, `plugin-dev`, `version-control`
- Descriptive of scope, not implementation
- No `k3m-` prefix (the marketplace name provides namespace)

### Skill naming
- kebab-case matching the directory name: `hook-development`, `scope-validation`
- Action-oriented when possible: `feedback-capture`, `staleness-check`

### Command naming
- kebab-case: `register`, `validate`, `feedback`, `optimize`
- Verb-first for actions: `check-staleness`, `update-refs`

### File naming
- Markdown files: kebab-case with `.md` extension
- YAML files: kebab-case with `.yaml` extension
- Scripts: kebab-case with appropriate extension (`.sh`, `.py`)
- Feedback entries: `{ISO-timestamp}_{component-name}.yaml`

### Version conventions
- All plugins start at `0.1.0` (pre-stable during infrastructure buildout)
- Bump to `1.0.0` after Step 8 end-to-end validation passes
- Follow semver: MAJOR for breaking changes, MINOR for features, PATCH for fixes

---

## 7. Plugin Independence (NF2)

Per the PRD's non-functional requirement NF2, each plugin must be independently installable. This means:

- **No hard dependencies:** A plugin must function without any other K3M plugin installed.
- **Graceful degradation:** If shared references aren't available (e.g., symlink broken after cache copy issue), the plugin should still work — just with potentially stale reference material.
- **Self-contained fallbacks:** Each plugin should include essential reference material inline in SKILL.md (core concepts, most common patterns). The shared references provide comprehensive detail, not basic functionality.

### How this works with shared references

The symlink pattern provides shared references when available, but each plugin's SKILL.md must contain enough core content to be useful standalone. The shared `docs/` files provide depth; the SKILL.md provides breadth. If the symlink is broken, the plugin works — just with less reference depth.

---

## 8. Marketplace.json Structure

```json
{
  "name": "k3m-marketplace",
  "owner": {
    "name": "Karim",
    "email": "karim.stekelenburg@me.com"
  },
  "metadata": {
    "description": "Personal plugin marketplace with self-maintaining infrastructure",
    "version": "0.1.0",
    "pluginRoot": "./plugins"
  },
  "plugins": [
    {
      "name": "meta-dev",
      "source": "./plugins/meta-dev",
      "description": "Marketplace infrastructure: organization, feedback, and maintenance",
      "version": "0.1.0",
      "category": "infrastructure",
      "tags": ["marketplace", "organization", "feedback", "maintenance"]
    },
    {
      "name": "plugin-dev",
      "source": "./plugins/plugin-dev",
      "description": "Plugin development toolkit with current Claude Code platform knowledge",
      "version": "0.1.0",
      "category": "development",
      "tags": ["plugin", "development", "scaffolding", "evaluation"]
    }
  ]
}
```

---

## 9. Design Decisions Log

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Scope declaration | Keywords + natural language + does_not_own | Keywords only; taxonomy; pure NL | Keywords enable fast filtering; NL handles nuance; does_not_own prevents scope creep |
| Shared refs access | Symlinks from plugin to shared/ | CLAUDE.md includes; copied docs; no sharing | Symlinks work in both dev and installed mode; single source of truth |
| Feedback storage | Central dir, one YAML per entry | Per-plugin files; single JSON; database | Fire-and-forget writes; easy cross-plugin queries; human-readable |
| Reference index | YAML with URLs + timestamps + local docs | JSON; markdown with links; database | YAML is readable; structured enough for automated processing |
| Registry format | YAML at marketplace root | JSON; database; per-plugin declarations only | Human-editable; single file for cross-plugin queries; YAML supports multi-line |
