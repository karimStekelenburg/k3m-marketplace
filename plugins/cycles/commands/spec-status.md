---
name: spec-status
description: Display the current status of a spec's implementation tracker — shows task progress, blockers, and verification state.
---

# Spec Status

Quick read-only view of spec implementation progress.

## Usage

`/spec-status` — show status for the active tracker (most recently updated)
`/spec-status <version>` — show status for a specific version

## Backend

```!
source "$CLAUDE_PLUGIN_ROOT/scripts/detect-backend.sh"
source "$K3M_BACKEND_SCRIPT"
```

## Workflow

1. **Find tracker:**
   - **fs:** Most recently modified `.yaml` in `docs/tracking/`
   - **github:** Find milestone issue, read tracker from marked comment

2. **Read the tracker.**

3. **Display summary table:**

```
## v{X.Y.0} — {Name}

| # | Task | Status | Proof |
|---|------|--------|-------|
| 1 | {title} | {status emoji} | {proof or "—"} |

**Progress:** {verified}/{total} verified · {implemented}/{total} implemented · {blocked} blocked
**Complete:** {yes/no}
```

Status emojis: `[ ]` pending, `[~]` in_progress, `[*]` implemented, `[x]` verified, `[!]` blocked

4. If blockers exist, list them with notes.
5. If all verified, display completion confirmation.

## Guidelines

- Read-only — never modify the tracker
- Keep output concise
