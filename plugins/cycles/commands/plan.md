---
name: plan
description: Convert a technical specification into a sequenced implementation plan with discrete, trackable tasks. Reads the spec and codebase to produce an ordered plan.
---

# Implementation Planner

Convert a technical specification into a concrete implementation plan.

## Inputs

The user provides a spec reference (e.g., "v0.1", a file path) or asks to "plan the current spec."

## Backend

```!
source "$CLAUDE_PLUGIN_ROOT/scripts/detect-backend.sh"
source "$K3M_BACKEND_SCRIPT"
```

## Workflow

1. **Read the spec** via the backend — understand every deliverable and acceptance criterion.

2. **Read relevant source code** — understand what exists, what needs to change, what's new.

3. **Generate the plan** with this structure:

```markdown
# Implementation Plan: v{X.Y.0} — {Milestone Name}

> **Spec:** {spec location}
> **Date:** {today}
> **Estimated tasks:** {count}

## Prerequisites

## Task sequence

### Task 1: {Short title}
- **Files:** {new/modified files}
- **Description:** {specific enough to be unambiguous}
- **Depends on:** {task numbers, or "none"}
- **Acceptance test:** {maps to spec acceptance criteria}

### Task 2: ...

## Integration verification

## Risk notes
```

4. **Write the plan:**
   - **fs:** Write to `docs/plans/v{X.Y}-{kebab-case-name}.md`
   - **github:** Post as marked comment (`<!-- k3m:plan -->`) on the milestone issue

5. **Report** the plan summary.

## Guidelines

- Tasks should be small enough to implement in a single focused session (30-90 min)
- Order tasks by dependency
- Each task must have a concrete acceptance test
- Include a task for updating the playground
- Include a final integration verification task
- Prefer 5-12 tasks per plan
