---
name: rup-init
description: Initialize a new RUP development cycle
argument-hint: "<cycle_type: initial | evolution | maintenance>"
allowed-tools: ["Bash", "Read", "Write"]
---

Initialize a new RUP development cycle. The argument specifies the cycle type:

- **initial** — First development cycle for a new product
- **evolution** — Adding features or major changes to an existing system
- **maintenance** — Bug fixes, patches, minor improvements

## Instructions

1. Parse the cycle type from `$1`. If not provided, ask the user which cycle type to use, explaining the three options.

2. Run the initialization script:
   ```bash
   bash ${CLAUDE_PLUGIN_ROOT}/scripts/init-cycle.sh <cycle_type>
   ```

3. If the script reports an existing cycle, inform the user and ask how to proceed (archive the old state or abort).

4. After successful initialization, read the state file to confirm:
   ```bash
   bash ${CLAUDE_PLUGIN_ROOT}/scripts/state.sh get
   ```

5. Present a summary to the user:
   - Cycle type and starting phase
   - Directory structure created
   - What happens next (Inception phase activities)
   - Remind them that `/rup-status` shows current state and `/rup-gate` evaluates milestones

6. The RUP lifecycle skill will auto-activate from this point forward, providing phase-aware guidance throughout the project.
