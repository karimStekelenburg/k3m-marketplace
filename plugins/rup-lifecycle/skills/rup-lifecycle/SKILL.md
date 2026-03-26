---
name: RUP Lifecycle
description: >-
  This skill should be used when the user asks about "project lifecycle", "RUP process",
  "development phases", "inception", "elaboration", "construction", "transition",
  "milestone gate", "iteration planning", "artifact status", "cycle status",
  or when working within an active RUP development cycle. Provides the complete
  Rational Unified Process state machine, phase coordination, artifact tracking,
  and autonomous orchestration for iterative software development.
version: 0.1.0
---

# RUP Lifecycle Management

Operate as a RUP-aware orchestrator when a cycle is active. Inform every action by the current phase, iteration, and artifact state.

## Quick Reference

### State Machine

```
INCEPTION → [gate] → ELABORATION → [gate] → CONSTRUCTION → [gate] → TRANSITION → [gate] → DONE
```

Each phase has defined departments (PM, SA, ENG, QA, OPS), required artifacts, and exit criteria. Gates are the only mechanism for phase advancement — no phase work may begin until the prior gate is approved.

### Cycle Types

- **initial** — First development cycle. Full process, all phases weighted equally.
- **evolution** — Adding features or major changes to existing system. Inception is lighter (vision already exists), Elaboration focuses on delta architecture.
- **maintenance** — Bug fixes, patches, minor improvements. Inception and Elaboration are minimal; Construction and Transition dominate.

## State Management

The cycle state lives in `.claude/rup-state.json`. Read and modify it using the state script:

```bash
# Read current state
bash ${CLAUDE_PLUGIN_ROOT}/scripts/state.sh get

# Read specific field
bash ${CLAUDE_PLUGIN_ROOT}/scripts/state.sh get phase

# Update a field
bash ${CLAUDE_PLUGIN_ROOT}/scripts/state.sh set phase elaboration
bash ${CLAUDE_PLUGIN_ROOT}/scripts/state.sh set iteration 2

# Update artifact status
bash ${CLAUDE_PLUGIN_ROOT}/scripts/state.sh artifact vision draft artifacts/inception/vision.md
bash ${CLAUDE_PLUGIN_ROOT}/scripts/state.sh artifact vision approved

# Record gate result
bash ${CLAUDE_PLUGIN_ROOT}/scripts/state.sh gate-record inception passed "All criteria met"
```

At the start of any session involving project work, read the state file to establish context. If no state file exists and the user is discussing project lifecycle, suggest running `/rup-init`.

## Phase Behavior

### Inception & Elaboration — Collaborative Mode

During these phases, act as an **interviewer and advisor**:

- Ask probing questions to extract requirements, constraints, and priorities
- Suggest alternatives and challenge assumptions
- Document ideas, decisions, and rationale in artifacts
- Track all ideas but flag scope creep — prioritize and defer aggressively, as many ideas will surface that don't belong in the current cycle
- Write artifacts to disk as drafts, updating status via the state script
- Present artifacts for review when the user is ready

Do NOT proceed autonomously. Wait for user direction. The user drives the process.

### Construction & Transition — Autonomous Mode

After the Elaboration gate is approved, shift to autonomous operation:

- Read the approved artifacts (requirements, architecture, dev-plan) as the work specification
- Plan iterations based on the development plan
- Dispatch the `artifact-writer` agent for structured document generation
- Create iteration subdirectories: `artifacts/construction/iteration-N/`
- Write iteration plans and assessments
- Contact the user ONLY at these moments:
  - **Iteration reviews** — present completed work for feedback
  - **Blocking decisions** — architectural questions not covered by approved artifacts
  - **Gate evaluations** — when ready to request phase transition
  - **Critical failures** — when something fundamentally breaks the plan

Between contact moments, proceed with implementation work without asking for permission.

## Enforcement Rules

**CRITICAL — These rules override default behavior:**

1. **No phase skipping.** Never begin work that belongs to a future phase. If in Inception, do not write architecture documents. If in Elaboration, do not begin implementation.
2. **No gate bypassing.** Phase transition happens ONLY through `/rup-gate` with a passing result. Never manually set the phase to the next value without gate validation.
3. **No premature completion.** Do not stop or declare work complete while required artifacts for the current phase are still pending. Check artifact status before concluding any work session.
4. **Artifact status integrity.** Only move artifacts through the valid status chain: `pending → draft → review → approved`. Never skip statuses.

## Artifact Protocol

Artifacts are bundled markdown files organized by phase. Each file may contain multiple related sections.

### File Map

| File                                               | Phase   | Contains                               |
| -------------------------------------------------- | ------- | -------------------------------------- |
| `artifacts/inception/vision.md`                    | INC     | Vision, Glossary, Stakeholder Requests |
| `artifacts/inception/risk-list.md`                 | INC→ALL | Risk List (living document)            |
| `artifacts/elaboration/requirements.md`            | ELB     | Use-Case Specs, Supplementary Spec     |
| `artifacts/elaboration/architecture.md`            | ELB     | Software Architecture Document         |
| `artifacts/elaboration/dev-plan.md`                | ELB     | Development Plan, Test Strategy        |
| `artifacts/construction/build-plan.md`             | CON     | Integration Build Plan                 |
| `artifacts/construction/iteration-N/plan.md`       | CON     | Iteration Plan                         |
| `artifacts/construction/iteration-N/assessment.md` | CON     | Iteration Assessment                   |
| `artifacts/transition/release.md`                  | TRN     | Deployment Plan, Release Notes         |

To create artifacts from templates:
```bash
# Templates are in the plugin's assets directory
ls ${CLAUDE_PLUGIN_ROOT}/skills/rup-lifecycle/assets/templates/
```

Read the template, adapt it to the project context, and write it to the artifact path. Update status via the state script.

### Gate Criteria

Validate gate readiness:
```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate-gate.sh
```

For detailed gate criteria per phase, consult `references/phases.md`.

## Departments × Phases

Five departments contribute across all phases with varying intensity:

| Dept | INC    | ELB    | CON    | TRN    |
| ---- | ------ | ------ | ------ | ------ |
| PM   | ██████ | ████   | ██     | ██     |
| SA   | ████   | ██████ | ██     | █      |
| ENG  | █      | ████   | ██████ | ████   |
| QA   | █      | ███    | █████  | ████   |
| OPS  | █      | █      | ███    | ██████ |

For the full task matrix, consult `references/departments.md`.

## Additional Resources

### Reference Files

For detailed specifications, consult:
- **`references/phases.md`** — Phase definitions, objectives, gate criteria, iteration patterns
- **`references/departments.md`** — Department × phase task matrix with specific deliverables
- **`references/artifacts.md`** — Artifact schemas, status rules, bundling details
- **`references/coordination.md`** — Contact moments, autonomy rules, recovery procedures

### Asset Files

- **`assets/templates/`** — Base templates for all artifact files

### Scripts

- **`${CLAUDE_PLUGIN_ROOT}/scripts/state.sh`** — State file CRUD operations
- **`${CLAUDE_PLUGIN_ROOT}/scripts/init-cycle.sh`** — Bootstrap new cycle
- **`${CLAUDE_PLUGIN_ROOT}/scripts/validate-gate.sh`** — Gate exit criteria validation
