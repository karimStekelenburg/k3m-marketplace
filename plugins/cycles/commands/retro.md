---
name: retro
description: Review how a cycle ran and improve automation skills. Collects signals from the tracker and git history, diagnoses issues, proposes changes, and A/B tests them via skill evals. Only keeps changes that measurably improve or maintain quality.
---

# Retro

Post-cycle retrospective that reviews automation performance and self-improves.

## Usage

`/retro` — Review the most recent completed cycle
`/retro <version>` — Review a specific cycle
`/retro dry-run` — Analyze and propose changes but don't apply

## Backend

```
source "$CLAUDE_PLUGIN_ROOT/scripts/detect-backend.sh" && source "$K3M_BACKEND_SCRIPT"
```

## Workflow

### Step 1: Collect signals

Read the tracker for the target cycle and gather:
- **Re-review count:** Phase 4 iterations before approval
- **Fix loop count:** Phase 6 iterations
- **Verification methods:** test-writer vs verification-gate vs ui-verifier
- **Blocked tasks:** count and reasons
- **Manual interventions:** did the cycle pause?

Read git log for the session:
- Commit count, fixup commits, reverts
- Rework indicators ("fix: ..." right after "feat: ...")

Read the active command files from `$CLAUDE_PLUGIN_ROOT/commands/`.

### Step 2: Diagnose

Categorize: skill gap, efficiency loss, robustness issue, context bloat.

**Skip criteria:** If cycle had zero issues, output:
```
Clean cycle — no automation improvements needed.
```

### Step 3: Propose changes

Max 5 proposals, each with: skill, type (fix/optimize/robustness/trim), diagnosis, change, expected impact.

Never propose changes to `/retro` itself.

### Step 4: A/B test via skill evaluations

For each proposal:
1. Check for existing eval
2. Record baseline score
3. Apply change
4. Run eval again
5. Keep if score improves or stays equal; revert if decreases
6. No eval possible → keep only if type is `fix`

### Step 5: Report

```
## Retro: v{X.Y} — {Name}

**Cycle stats:** review iterations, fix loops, manual interventions, blocked tasks

| # | Change | Skill | Type | Eval | Applied? |
|---|--------|-------|------|------|----------|

**Net result:** {n} applied, {m} reverted, {k} skipped
```

### Step 6: Update state

- **github:** Add `retro-done` label to the milestone issue

## Guidelines

- Small wins compound — don't aim for perfection
- Eval gate is non-negotiable for non-fix changes
- Trust data over intuition
- Optimize for all future cycles, not just the one that ran
- Flag fundamental restructures for the user
