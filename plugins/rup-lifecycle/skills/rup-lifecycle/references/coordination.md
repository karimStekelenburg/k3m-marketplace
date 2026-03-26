# Coordination Protocol — Detailed Reference

## Operating Modes

The RUP lifecycle has two distinct operating modes based on the current phase.

### Collaborative Mode (Inception & Elaboration)

The user drives the process. The agent acts as an interviewer, advisor, and documenter.

#### Interviewing Approach

When gathering requirements and defining the vision:

1. **Start broad, then narrow.** Begin with open-ended questions ("What problem are we solving?"), then drill into specifics ("What happens when a user tries to X without Y?").
2. **Challenge assumptions.** When the user states a requirement, ask "why" at least once. Surface the underlying need.
3. **Suggest alternatives.** If the user proposes a solution, offer at least one alternative approach before documenting the choice.
4. **Document as you go.** After each discussion, update the relevant artifact draft. Don't wait until the end.
5. **Summarize periodically.** Every 3-5 exchanges, provide a brief summary of decisions made and open questions remaining.

#### Scope Guardianship

The user will generate many ideas. Not all belong in the current cycle.

- Track all ideas, even deferred ones (in a "Deferred Ideas" section of vision.md)
- For each new idea, evaluate against:
  - Does it align with the stated vision?
  - Does it fit within the estimated timeline/resources?
  - Is it a must-have or a nice-to-have?
  - Does it increase risk significantly?
- Be direct when scope is expanding: "This is a valuable idea, but adding it would [impact]. I'd recommend deferring it to a future cycle."
- At gate evaluation, be strict: only approved-scope items count toward exit criteria

#### Contact Rhythm

During Collaborative Mode, every interaction is a contact moment. There is no autonomous work — all progress requires user participation.

### Autonomous Mode (Construction & Transition)

The agent drives the process. The user is consulted only at defined contact moments.

#### Autonomous Work Pattern

Between contact moments, follow this loop:

1. Read the current iteration plan
2. Pick the next unfinished item
3. Implement it (code, tests, configuration)
4. Update artifact status
5. If blocked → contact user (see Contact Moments below)
6. When iteration scope is complete → write assessment → contact user for review

#### Contact Moments

These are the ONLY times to engage the user during autonomous mode:

| Moment | Trigger | What to Present |
|--------|---------|----------------|
| **Iteration Review** | Iteration scope complete | Assessment, demo of work, metrics |
| **Blocking Decision** | Question not answerable from approved artifacts | Specific question with options and recommendation |
| **Gate Evaluation** | Ready to transition phase | Gate validation results, recommendation |
| **Critical Failure** | Plan is no longer viable | What broke, impact, proposed recovery |
| **Risk Escalation** | New high-impact risk discovered | Risk details, mitigation options |

#### What Does NOT Require User Contact

- Implementation decisions within the approved architecture
- Bug fixes for issues discovered during testing
- Refactoring that doesn't change interfaces
- Test failures and their resolution
- Iteration planning within the approved dev-plan scope
- Updating artifact status from draft → review
- Creating new iteration subdirectories

## Recovery Procedures

### Lost State

If `.claude/rup-state.json` is missing or corrupted:

1. Check git history for the last known good state
2. If recoverable, restore the file
3. If not recoverable, assess the artifact directory structure to infer current phase
4. Reconstruct state from artifacts: check which files exist and their content completeness
5. Ask the user to confirm the reconstructed state

### Unexpected Phase State

If the artifacts don't match the recorded phase (e.g., state says "construction" but no approved architecture):

1. Do NOT proceed with current-phase work
2. Report the inconsistency to the user
3. Recommend either:
   - Rolling back the phase to match artifact reality
   - Fast-tracking the missing artifacts if content exists but status wasn't updated

### Mid-Iteration Interruption

If a session ends mid-iteration:

1. On next session start, read state file
2. Check iteration plan vs. completed work
3. Resume from where work was interrupted
4. Do NOT restart the iteration

## Agent Dispatch

### When to Use artifact-writer

Dispatch the `artifact-writer` agent for:

- Initial creation of any artifact from template
- Major artifact revisions (not minor edits)
- Artifacts that require synthesizing multiple inputs (e.g., architecture doc from requirements + risk list)

Do NOT use artifact-writer for:
- Status updates to the state file
- Minor text edits to existing artifacts
- Iteration plans (these are short enough to write inline)

### Dispatch Pattern

```
1. Read the relevant template from assets/templates/
2. Read all input artifacts the writer needs
3. Dispatch artifact-writer with:
   - Template content
   - Input artifacts
   - Current phase and iteration context
   - Specific instructions for what to produce
4. When agent returns, review the output
5. Write to disk and update state
```

## Gate Evaluation Protocol

When the user invokes `/rup-gate` or when autonomous mode determines gate readiness:

1. Run `validate-gate.sh` to get structured pass/fail results
2. For each failing check:
   - Explain what's missing and why it matters
   - Estimate effort to complete
3. For passing checks:
   - Briefly confirm completion
4. Provide an overall recommendation:
   - **Pass** — all criteria met, recommend advancing
   - **Conditional pass** — minor items outstanding, can advance with follow-up
   - **Fail** — significant gaps, list what needs to happen before re-evaluation
5. If the gate passes and the user approves:
   - Record the gate result via `state.sh gate-record`
   - Advance the phase via `state.sh set phase <next>`
   - If entering Construction, shift to Autonomous Mode
