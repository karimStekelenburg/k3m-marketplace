---
name: cycle
description: Run a full spec implementation cycle — plan, track, implement, review, test, verify, and confirm. Orchestrates all skills and subagents in sequence with a review-fix-reverify loop.
---

# Cycle

Run a complete spec-to-verified implementation cycle. This is the orchestrator that ties together all skills and subagents.

## Usage

`/cycle <spec-ref>` — Run the full cycle for a spec (e.g., "v0.2", "canvas-viewport")
`/cycle resume` — Resume an in-progress cycle (reads the most recent tracker)
`/cycle` — (no args) Auto-detect the next milestone to implement

## Backend Detection

Before starting, detect which backend to use. Run this as a single Bash command:

```
source "$CLAUDE_PLUGIN_ROOT/scripts/detect-backend.sh" && source "$CLAUDE_PLUGIN_ROOT/scripts/backend-${K3M_BACKEND}.sh" && source "$CLAUDE_PLUGIN_ROOT/scripts/state-machine.sh" && echo "Backend: $K3M_BACKEND"
```

- **`fs`** (default, local): Reads/writes `docs/specs/`, `docs/plans/`, `docs/tracking/`, `docs/ROADMAP.md`
- **`github`** (CI / GitHub Actions): Reads/writes via GitHub API — specs, plans, and trackers stored as marked comments on milestone issues. State tracked via issue labels.

Valid transitions:
```
unspecified → specced → planned → tracked → implementing → reviewing → testing → verified → complete → retro-done
                                             ↑ review rejected ←─── reviewing
                                             ↑ test failed ←────── testing
```

Before each phase, validate the transition:
```bash
k3m_check_transition "$current_state" "$target_state"
```

## Auto-Detection (no args)

When invoked without a spec reference:

1. **Check for in-progress work:** Look for trackers where `summary.complete: false`. If found, resume the most recent one (same as `/cycle resume`).
   - **fs:** Check `docs/tracking/` for incomplete trackers
   - **github:** Check issues with `implementing` or `testing` labels

2. **Conflict guard — check for parallel work BEFORE starting:**
   Before selecting the next milestone, run ALL of these checks. If any fails, stop and report — do NOT proceed to implementation.

   a. **Check open PRs:** Run `gh pr list --state open` and inspect titles/branches. If any open PR targets the same milestone (by version number or name), STOP and output:
      `"⚠ PR #{number} is already in progress for this milestone: {title}. Aborting to avoid duplicate work."`

   b. **Check recently merged PRs:** Run `gh pr list --state merged --limit 10` and check if the milestone was just merged. Also run `git fetch origin main && git log origin/main --oneline -10` to see if a commit message references the milestone. If the milestone is already on main, STOP and output:
      `"⚠ Milestone {version} was already merged to main via {commit/PR}. Skipping to the next milestone."`
      Then re-run auto-detection skipping this milestone.

   c. **Check other worktrees:** Run `git worktree list` and check if any other worktree has uncommitted changes or a branch name containing the milestone version. If so, WARN the user:
      `"⚠ Worktree {path} on branch {branch} may be working on this milestone. Proceed? (y/n)"`

3. **Find next unspecified milestone:**
   - **fs:** Read `docs/ROADMAP.md`, walk dependency graph, find first milestone whose dependencies are complete but has no spec/plan/tracker
   - **github:** List milestone issues, check state labels, find first `unspecified` issue whose dependency issues are `complete`

4. **Roadmap exhausted:** If ALL milestones are complete:
   - Output: "All roadmap milestones are complete. Run `/roadmap extend` to plan the next phase."
   - Do NOT proceed — the user must consciously decide what comes next.

## Full Cycle Phases

### Phase 0: Spec (conditional — runs automatically)
1. Only runs if auto-detection found a milestone with no spec
2. Generate the spec inline — follow the spec skill's workflow directly. Do NOT use the Skill tool.
3. Write the spec via the backend:
   - **fs:** Write to `docs/specs/v{X.Y}-{name}.md`
   - **github:** Post as marked comment on the milestone issue
4. Validate transition: `k3m_check_transition "unspecified" "specced"`
5. Continue immediately to Phase 1

### Phase 1: Plan
1. Generate the implementation plan inline. Do NOT use the Skill tool.
2. If a plan already exists (check via backend), skip this step
3. Write the plan via the backend
4. Validate transition: `k3m_check_transition "specced" "planned"`

### Phase 2: Track + Claim
1. Initialize the tracker from the plan
2. If a tracker already exists, skip this step
3. Write the tracker via the backend
4. Validate transition: `k3m_check_transition "planned" "tracked"`
5. Claim the milestone:
   - **fs:** `git add docs/ && git commit && git push`
   - **github:** Set `implementing` label, assign self, update project board status

### Phase 3: Implement
For each task in the tracker (in order):
1. Update tracker: task status → `in_progress`
2. Implement the task according to the plan
3. Update tracker: task status → `implemented`, fill `files` field
4. Run `bunx tsc --noEmit` after each task — if it fails, fix before moving on

### Phase 4: Review + Fix Loop
1. Validate transition: `k3m_check_transition "implementing" "reviewing"`
2. Launch **code-reviewer** subagent with all implementation files and the spec
3. If review returns **YES**: proceed to Phase 5
4. If review returns **YES WITH CHANGES** or **NO**:
   a. Fix all critical and major issues
   b. Transition back: `k3m_check_transition "reviewing" "implementing"` → then back to reviewing
   c. Re-launch code-reviewer with "re-review after fixes" prompt
   d. Repeat until approved (max 3 iterations, then ask user)

### Phase 5: Test + Verify
1. Validate transition: `k3m_check_transition "reviewing" "testing"`
2. Launch **test-writer** subagent to write and run tests
3. Launch **verification-gate** subagent on remaining `implemented` tasks
4. If tasks have `requires_ui_verification: true`:
   a. Launch **ui-verifier** subagent

### Phase 6: Fix Failures Loop
If any tasks are still `implemented` (not `verified`):
1. Read failure notes from tracker
2. Fix the issues
3. Transition: `k3m_check_transition "testing" "implementing"` → fix → back to testing
4. Re-run verification-gate on failed tasks only
5. Repeat until all pass (max 3 iterations, then ask user)

### Phase 7: Confirm
1. Validate transition: `k3m_check_transition "testing" "verified"`
2. Display final status (run spec-status logic inline)
3. Verify all tasks are verified
4. If complete: output "Cycle complete. All {n} tasks verified."
5. Create a PR:
   - PR body MUST contain `Closes #N` referencing the milestone issue
   - **github:** Update issue state to `complete`
6. If not complete: list remaining unverified tasks and ask user

### Phase 8: Retrospective (automatic)
1. Validate transition: `k3m_check_transition "verified" "complete"` then `k3m_check_transition "complete" "retro-done"`
2. Run the retro workflow inline. Do NOT use the Skill tool.
3. Collect signals, diagnose, propose changes, eval, apply
4. Update state:
   - **github:** Set `retro-done` label
5. This phase is mandatory. The cycle is not complete until the retro has run.

## Resume Protocol

When invoked with `/cycle resume`:
1. Find the most recently updated tracker
2. Determine current state:
   - **fs:** `k3m_current_state_fs "$version"`
   - **github:** `k3m_current_state_gh "$issue_number"`
3. Map state to phase:
   - `tracked` → Phase 3 (implement)
   - `implementing` → Phase 3 (continue)
   - `reviewing` → Phase 4
   - `testing` → Phase 5
   - `verified` → Phase 7 (confirm)
4. Resume from that phase

## Parallel Execution

Where possible, launch subagents in parallel:
- **Phase 4+5**: code-reviewer and test-writer can run simultaneously
- **Phase 5**: test-writer and verification-gate can run in parallel if they cover different tasks

## Error Handling

- If `bunx tsc --noEmit` fails during implementation: fix immediately, don't proceed
- If a subagent fails to return: report the failure and ask user
- If the fix loop exceeds 3 iterations: stop and ask user for guidance
- If a task is `blocked`: skip it, continue with other tasks, report at end
- If a state transition is invalid: STOP and report the invalid transition — never force it

## Guidelines

- **The cycle is fully automatic.** A single `/cycle` invocation runs ALL phases from spec through retro without requiring the user to re-invoke any sub-skill.
- **Execute sub-skill logic inline** — do NOT use the Skill tool to invoke /spec, /plan, or /retro.
- Always update the tracker at every state change — it's the source of truth
- Never skip phases — even if you think tests aren't needed, run them
- The cycle is complete ONLY when all tasks are verified AND the retro has run
- Keep the user informed at phase transitions with a one-line status update
- If something unexpected happens, pause and ask rather than guessing
