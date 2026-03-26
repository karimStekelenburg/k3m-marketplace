---
name: spec-tracker
description: Initialize or update a task tracker for a spec's implementation plan. Extracts tasks from the plan and creates a YAML tracker file with status, proof, and verification fields.
---

# Spec Tracker

Manage task tracking for spec implementation with verification gates.

## Backend

```!
source "$CLAUDE_PLUGIN_ROOT/scripts/detect-backend.sh"
source "$K3M_BACKEND_SCRIPT"
```

## Commands

### Initialize tracker: `/spec-tracker init <plan-ref>`

1. **Read the plan** via the backend
2. **Extract all tasks** into a YAML tracker
3. **Classify each task's verification method** based on its acceptance test text:
   - UI keywords (`playground`, `UI`, `visual`, `screenshot`, `browser`, `click`, `interaction`, `animation`, `render`) → `requires_ui_verification: true`
   - Test keywords (`test`, `assert`, `return`, `throw`, `compile`, `pass`) → `requires_unit_test: true`
   - Both can be true
4. **Write tracker:**
   - **fs:** Write to `docs/tracking/v{X.Y}-{name}.yaml`
   - **github:** Post as marked comment (`<!-- k3m:tracker -->`) on the milestone issue, with YAML in a code fence

Tracker format:

```yaml
spec: v{X.Y.0}
name: {Milestone Name}
plan: {plan location}
spec_file: {spec location}
created: {ISO date}
updated: {ISO date}

tasks:
  - id: 1
    title: "{Task title from plan}"
    status: pending          # pending | in_progress | implemented | verified | blocked
    files: []
    acceptance_test: "{from plan}"
    requires_unit_test: true
    requires_ui_verification: false
    proof: null
    verified_by: null
    notes: null

summary:
  total: {n}
  pending: {n}
  in_progress: 0
  implemented: 0
  verified: 0
  blocked: 0
  needs_ui_verification: {count}
  complete: false
```

### Update task: `/spec-tracker update <task-id> <status> [notes]`

1. Read the tracker via backend
2. Update the specified task's status
3. If `blocked`, require notes
4. Recalculate summary counts
5. Update `updated` timestamp
6. Write back via backend

### Mark verified: `/spec-tracker verify <task-id> <proof> <verified_by>`

1. Read tracker
2. Set status to `verified`, fill `proof` and `verified_by`
3. Recalculate summary
4. If ALL verified → set `summary.complete: true`
5. Write back

## Guidelines

- Never skip from `pending` to `verified` — must go through `implemented`
- The `proof` field must contain concrete evidence
- Tasks with `requires_ui_verification: true` are NOT fully verified until ui-verifier has run
