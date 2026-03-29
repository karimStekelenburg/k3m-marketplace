---
name: report-issue
description: >-
  This skill should be used when the user says "plugin-dev got this wrong",
  "plugin-dev is missing X", "report an issue with plugin-dev",
  "plugin-dev told me the wrong thing", or invokes /plugin-dev-sync:report-issue.
  Provides guided feedback collection and triggers automatic root-cause
  analysis, patching, and PR creation.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - WebFetch
argument-hint: "<description of what went wrong>"
---

# Report Issue

Collect structured feedback about plugin-dev failures and trigger an automated
fix pipeline that patches both plugin-dev and plugin-dev-sync if needed.

## Feedback Collection

When invoked, gather the following from the user's report:

1. **What happened**: What did plugin-dev do wrong or miss?
2. **What was expected**: What should it have done instead?
3. **Context**: Which skill/agent/command was involved?
4. **Evidence** (optional): Links, docs, or examples proving the correct behavior

If the user's initial report is vague, ask one focused clarifying question.
Do not ask more than one follow-up.

## Structured Issue Format

Compile the feedback into a structured issue:

```markdown
## Issue Report

- **Reporter**: user
- **Date**: YYYY-MM-DD
- **Component**: skill/agent name
- **Symptom**: what went wrong
- **Expected**: what should have happened
- **Evidence**: links or references
```

## Automated Fix Pipeline

After collecting the issue, launch the **issue-analyst** agent with the
structured issue. The agent will:

1. **Diagnose**: Identify the root cause in plugin-dev (wrong info in a skill,
   missing reference, outdated example, weak trigger description, etc.)
2. **Verify**: Cross-reference against official sources to confirm the correct
   information. Fetch relevant docs if needed.
3. **Patch plugin-dev**: Apply the fix to the appropriate files
4. **Validate**: Run `claude plugin validate` on plugin-dev
5. **Check plugin-dev-sync**: Determine if the bug was introduced by a previous
   plugin-dev-sync sync (check git blame). If so, identify what went wrong in
   plugin-dev-sync's discovery/review pipeline and patch it too.
6. **Commit and PR**: Create a branch, commit changes, and open a PR with:
   - The original issue report
   - Root cause analysis
   - What was fixed and where
   - Whether plugin-dev-sync was also patched and why
   - Validation results

## PR Branch Naming

`plugin-dev-sync/fix-<component>-<short-description>`

Example: `plugin-dev-sync/fix-hook-dev-missing-stop-event`

## When Meta-Dev Itself Needs Fixing

If the issue-analyst determines plugin-dev-sync's pipeline caused the problem
(e.g., the discovery-crawler missed a feature, or the diff-reviewer
approved a bad change), it should:

1. Identify which plugin-dev-sync component failed
2. Patch the relevant agent prompt or skill instructions
3. Include both plugin-dev and plugin-dev-sync changes in the same PR
4. Explain the plugin-dev-sync fix in the PR report
</description>