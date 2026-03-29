---
name: rup-gate
description: Evaluate milestone gate criteria for the current phase
allowed-tools: ["Bash", "Read", "Write"]
---

Evaluate whether the current phase's exit criteria are met and decide whether to advance to the next phase.

## Instructions

1. Read the current state:
   ```bash
   bash ${CLAUDE_PLUGIN_ROOT}/scripts/state.sh get
   ```

2. If no active cycle exists, inform the user and abort.

3. Run gate validation:
   ```bash
   bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate-gate.sh
   ```

4. Parse the JSON output and present results:

   **For each check:**
   - Show artifact name, required status, actual status, and pass/fail
   - For failing checks: explain what's missing and estimate effort to complete

   **Overall assessment:**
   - **Pass** — All criteria met. Recommend advancing to the next phase.
   - **Conditional pass** — Minor items outstanding. Can advance with explicit follow-up commitment.
   - **Fail** — Significant gaps. List concrete actions needed before re-evaluation.

5. **If the gate passes**, ask the user for approval to advance:
   - "Gate evaluation passed. Advance from [current] to [next] phase?"
   - On approval:
     ```bash
     bash ${CLAUDE_PLUGIN_ROOT}/scripts/state.sh gate-record <phase> passed "<notes>"
     bash ${CLAUDE_PLUGIN_ROOT}/scripts/state.sh set phase <next_phase>
     ```
   - If advancing to Construction, note the shift to autonomous mode

6. **If the gate fails**, do NOT offer to bypass or manually advance. List what needs to happen and offer to help complete the outstanding items.

7. Be strict during gate evaluation. The gate exists to protect project quality. Do not rubber-stamp incomplete work.
</next_phase></notes></phase>