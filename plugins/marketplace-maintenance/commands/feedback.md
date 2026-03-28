---
description: Capture feedback about a plugin or skill without interrupting your current task. Use when something is broken, suboptimal, or missing in a K3M marketplace plugin.
---

# Capture Feedback

Fire-and-forget feedback capture for K3M marketplace plugins. Record what's wrong without stopping your current work.

## Input

$ARGUMENTS should be the feedback text. Examples:
- `/marketplace-maintenance:feedback hook-development skill is missing FileChanged event type`
- `/marketplace-maintenance:feedback plugin-dev scaffolding doesn't include LSP configuration`
- `/marketplace-maintenance:feedback scope-validation flagged a false positive on shared config`

If no arguments are provided, prompt for:
1. Which plugin/component is the feedback about?
2. What's the issue?

## Process

### Step 1: Parse the feedback

Extract from $ARGUMENTS or prompting:
- **Plugin name:** Which plugin is this about? (auto-detect from context if possible)
- **Component:** Which skill/command/agent/hook? (auto-detect if mentioned)
- **Feedback text:** The actual issue description

### Step 2: Auto-classify

Based on the feedback text, suggest:
- **severity:** minor | moderate | major | critical
- **tags:** Auto-suggest from common categories:
  - `outdated-reference` — content doesn't match current platform capabilities
  - `missing-feature` — something that should be covered but isn't
  - `wrong-context` — skill activated in wrong situation or gave irrelevant guidance
  - `incorrect-info` — factually wrong information
  - `poor-structure` — content is hard to follow or poorly organized
  - `too-verbose` — too much content loaded when not needed
  - `too-terse` — not enough detail for the task at hand

### Step 3: Capture context

Auto-capture from the current session:
- **timestamp:** Current time in ISO format
- **session_type:** Infer from conversation context (development | prototyping | production | maintenance)
- **task:** Brief description of what the user was doing when they encountered the issue

### Step 4: Write feedback entry

Write a YAML file to `{marketplace_root}/feedback/{plugin-name}/`:
- Filename: `{ISO-timestamp}_{component-name}.yaml`
- Format per architecture.md section 5

### Step 5: Confirm briefly

Report in one line: "Feedback captured: {plugin}/{component} — {tag}. Continue working."

Do NOT elaborate, summarize, or suggest fixes. The entire point is minimal interruption.
