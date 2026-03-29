---
description: Process accumulated feedback and propose improvements to marketplace plugins. Use when ready to review and act on feedback collected via /feedback.
---

# Optimization Pass

Read accumulated feedback for a plugin or the entire marketplace, identify patterns, and propose concrete improvements. All proposals are presented for review before being applied (NF3).

## Input

$ARGUMENTS can be:
- A plugin name (e.g., `plugin-dev`) — optimize that specific plugin
- `all` or empty — optimize all plugins with pending feedback

## Process

### Step 1: Read feedback entries

Scan `{marketplace_root}/feedback/{plugin-name}/` for all entries with `status: open`.

If no feedback exists for the target, report that and exit.

### Step 2: Group by component

Group feedback entries by `component.name`:
```
plugin-dev:
  hook-development: [3 entries]
  skill-development: [1 entry]
  plugin-structure: [2 entries]
```

### Step 3: Identify patterns

For each component with multiple feedback entries, look for patterns:

**Common pattern types:**
- **Outdated reference** — Multiple entries mentioning missing or incorrect information about the same topic. Indicates the reference docs need updating.
- **Wrong context** — Entries saying the skill activated in wrong situations or gave irrelevant guidance. Indicates the description triggers need refinement.
- **Missing feature** — Entries requesting the same capability. Indicates a gap that should be addressed.
- **Too verbose/terse** — Entries about content length. Indicates progressive disclosure needs adjustment.
- **Structural issues** — Entries about organization, findability, or flow. Indicates the skill structure needs rework.

Use the `tags` field from feedback entries to accelerate pattern detection.

### Step 4: Propose improvements

For each identified pattern, propose a concrete change:

```
## Optimization Proposal: {component}

### Pattern identified
{N} feedback entries about: {pattern description}

### Evidence
- "{quote from feedback 1}" ({date})
- "{quote from feedback 2}" ({date})
- "{quote from feedback 3}" ({date})

### Proposed change
{Specific, actionable change to make}

### Files affected
- {file path 1}: {what changes}
- {file path 2}: {what changes}

### Risk assessment
{Low/Medium/High} — {reasoning}
```

### Step 5: Evaluate skill descriptions (where applicable)

For patterns related to triggering behavior (`wrong-context` tag), evaluate the skill description:

1. Collect the feedback entries as negative test cases (situations where the skill should NOT have triggered)
2. Review the current description's trigger phrases
3. Propose updated trigger phrases that would avoid the false triggers
4. If possible, also identify positive test cases from the feedback context
5. Present the before/after description with reasoning

### Step 6: Present for review

Present all proposals as a batch. For each proposal:
- Explain the pattern and evidence
- Show the proposed change
- Ask for approval to proceed

### Step 7: Apply approved changes

For each approved proposal:
1. Make the changes to the affected files
2. Update the feedback entries' `status` to `addressed` and set `resolution` to a brief description
3. Update the registry if component names or scope changed

### Step 8: Summary

Report what was changed:
```
## Optimization Summary

### Applied
- {component}: {brief description of change}

### Deferred
- {component}: {reason for deferral}

### Feedback resolved
- {N} entries marked as addressed
- {M} entries remaining open
```

## For single feedback entries

If a component has only one feedback entry, still propose an improvement — but flag that the pattern is based on a single data point and suggest waiting for more feedback before making structural changes.

## Key principles

1. **Evidence-based.** Every proposal must cite specific feedback entries.
2. **No silent changes.** Present everything for review.
3. **Prioritize patterns.** Multiple entries about the same issue = higher priority.
4. **Conservative changes.** Prefer targeted fixes over broad rewrites.
5. **Track resolutions.** Always update feedback status after changes are applied.
