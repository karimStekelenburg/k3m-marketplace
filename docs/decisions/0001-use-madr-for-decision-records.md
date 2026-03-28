---
status: accepted
date: 2026-03-28
decision-makers: [Karim]
---

# 0001 — Use MADR for Architecture Decision Records

## Context and Problem Statement

The K3M marketplace is growing in scope — multiple plugins, automated sync
pipelines, maintenance tooling. Design decisions are made in conversations and
PRs but not systematically recorded. Future contributors (including automated
agents) lack context on *why* things are the way they are.

We need a lightweight, version-controlled way to record architectural decisions
at both the marketplace level and within individual plugins.

## Decision Drivers

- Decisions should live alongside code in version control
- Format should be simple enough for both humans and AI agents to author
- Should work at two levels: marketplace-wide and per-plugin
- Minimal ceremony — we don't want ADRs to become a bottleneck

## Considered Options

1. MADR 4.0 (Markdown Any Decision Records)
2. Nygard-style ADRs (original lightweight format)
3. RFCs / design docs only

## Decision Outcome

Chosen option: "MADR 4.0", because it provides a structured template with YAML
frontmatter (machine-parseable status tracking), is widely adopted, and includes
optional sections that can be skipped for simple decisions.

### Consequences

- **Good**: Consistent format across marketplace and all plugins
- **Good**: YAML frontmatter enables automated status tracking and listing
- **Good**: Template is simple enough that the maintenance plugin can auto-generate ADRs
- **Bad**: Adds a directory and convention to learn for plugin authors

## Pros and Cons of the Options

### MADR 4.0

- **Good**: Structured YAML frontmatter for status, date, decision-makers
- **Good**: Flexible — minimal and full template variants
- **Good**: Active community and tooling support
- **Neutral**: Requires `docs/decisions/` directory convention

### Nygard-style ADRs

- **Good**: Extremely simple (Title, Status, Context, Decision, Consequences)
- **Bad**: No frontmatter — harder to parse programmatically
- **Bad**: No standard for decision drivers or options comparison

### RFCs / design docs only

- **Good**: More room for detailed analysis
- **Bad**: Too heavyweight for most plugin decisions
- **Bad**: No standard format — hard to list or track status
