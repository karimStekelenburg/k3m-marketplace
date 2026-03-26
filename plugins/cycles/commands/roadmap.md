---
name: roadmap
description: Brainstorm, create, or extend the project roadmap with new milestones. Use when the roadmap is exhausted, needs new versions, or when ideating future direction.
---

# Roadmap

Ideate, create, and extend the project roadmap.

## Usage

`/roadmap` — Review current roadmap status
`/roadmap extend` — Add next batch of milestones
`/roadmap brainstorm <topic>` — Brainstorm features for an area
`/roadmap create` — Create roadmap from scratch

## Backend

```
source "$CLAUDE_PLUGIN_ROOT/scripts/detect-backend.sh" && source "$K3M_BACKEND_SCRIPT"
```

## Workflow: `/roadmap` (status)

1. Read roadmap via `k3m_read_roadmap`
2. Read trackers to determine completion status
3. Output status table:
   ```
   | Version | Name | Status |
   |---------|------|--------|
   | v0.1.0 | Unified Window Manager | Complete |
   | v0.2.0 | Canvas Viewport | Spec ready |
   ```

## Workflow: `/roadmap extend`

1. **Read context:** roadmap, design doc, existing specs, src/
2. **Analyze gaps:** features in design doc not on roadmap, natural next steps, DX improvements
3. **Draft new milestones** with: version, name, dependency, deliverables, AC, playground update
4. **Present draft** to user before writing
5. **Update roadmap:**
   - **fs:** Append to `docs/ROADMAP.md`
   - **github:** Also create new milestone issues with `milestone` label

## Workflow: `/roadmap brainstorm <topic>`

1. Read context
2. Generate 5-10 concrete feature ideas
3. For each: what, why, effort (S/M/L/XL), dependencies, risk
4. Present as ranked list — ideation only, no file changes

## Workflow: `/roadmap create`

1. Read design doc or project vision
2. Ask 3 questions: first working thing, first users, rough timeline
3. Generate roadmap
4. Write to `docs/ROADMAP.md`
5. **github:** Also create milestone issues

## Guidelines

- Milestones should be independently shippable
- Each milestone should have a "demo moment"
- Keep dependency graph as linear as possible
- Don't plan more than 6 months ahead in detail
- Include effort estimates
