---
name: rup-status
description: Show current RUP cycle status and artifact state
allowed-tools: ["Bash", "Read"]
---

Display the current state of the RUP development cycle.

## Instructions

1. Read the current state:
   ```bash
   bash ${CLAUDE_PLUGIN_ROOT}/scripts/state.sh get
   ```

2. If no active cycle exists, inform the user and suggest running `/rup-init`.

3. Present a formatted status report:

   **Cycle Overview:**
   - Cycle type, current phase, iteration number
   - Start date and elapsed time

   **Artifact Status:**
   - Table of all artifacts with their status (pending/draft/review/approved)
   - Highlight which artifacts are required for the current phase's gate
   - Mark artifacts whose files exist on disk vs. those still missing

   **Gate Readiness:**
   - Run the gate validation to show current readiness:
     ```bash
     bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate-gate.sh 2>/dev/null || true
     ```
   - Show pass/fail for each gate criterion
   - Indicate what remains before the gate can be attempted

   **Gate History:**
   - List previous gate evaluations (if any) with dates and results

4. Keep the output concise but informative. Use tables and status indicators for scanability.
