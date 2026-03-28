---
description: Create or list architecture decision records (ADRs) for the marketplace. Use when a design decision is made, a structural change is proposed, or to review past decisions.
argument-hint: "[new <title>|list|status <NNNN> <accepted|superseded|deprecated>]"
---

# Architecture Decision Records

Maintain ADRs for the K3M marketplace in `docs/decisions/` using the
[MADR 4.0](https://adr.github.io/madr/) format.

## Input

$ARGUMENTS determines the action:
- `new <title>` — create a new ADR
- `list` — list all existing ADRs with status
- `status <NNNN> <accepted|superseded|deprecated>` — update an ADR's status

## Directory

ADRs live at the repository root in `docs/decisions/`:

```
docs/decisions/
├── 0001-use-madr-for-decision-records.md
├── 0002-plugin-scope-boundaries.md
└── ...
```

Create the directory if it doesn't exist.

## Creating a new ADR (`new`)

### Step 1: Determine the next number

Read existing files in `docs/decisions/` and find the highest `NNNN` prefix.
The new ADR gets `NNNN + 1`. If the directory is empty, start at `0001`.

### Step 2: Generate the filename

Convert the title to kebab-case:
```
"Use MADR for decision records" → 0001-use-madr-for-decision-records.md
```

### Step 3: Write the ADR

Use the MADR 4.0 template:

```markdown
---
status: proposed
date: YYYY-MM-DD
decision-makers: []
---

# NNNN — Title

## Context and Problem Statement

{Describe the context and the problem or question being addressed.}

## Decision Drivers

- {Driver 1}
- {Driver 2}

## Considered Options

1. {Option 1}
2. {Option 2}
3. {Option 3}

## Decision Outcome

Chosen option: "{Option N}", because {justification}.

### Consequences

- **Good**: {positive consequence}
- **Bad**: {negative consequence}

## Pros and Cons of the Options

### {Option 1}

- **Good**: {argument}
- **Bad**: {argument}

### {Option 2}

- **Good**: {argument}
- **Bad**: {argument}
```

### Step 4: Fill in content

Based on the conversation context, fill in as much of the template as possible.
Ask the user for any missing information. At minimum, the Context, Decision
Drivers, and Considered Options should be populated.

### Step 5: Commit and push via PR

```bash
BRANCH="docs/adr-NNNN-$(echo "$TITLE" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')"
git checkout -b "$BRANCH" main
git add "docs/decisions/NNNN-title.md"
git commit -m "docs(adr): NNNN — Title"
git push -u origin "$BRANCH"
gh pr create --title "docs(adr): NNNN — Title" --body "New architecture decision record."
```

Report the PR URL to the user.

## Listing ADRs (`list`)

Read all files in `docs/decisions/`, extract the `status` from YAML frontmatter,
and display a table:

```
 #    Status      Date        Title
0001  accepted    2026-03-28  Use MADR for decision records
0002  proposed    2026-03-28  Plugin scope boundaries
0003  deprecated  2026-03-20  Shared reference doc format
```

## Updating status (`status`)

Read the ADR file, update the `status` field in the YAML frontmatter, commit,
push, and create a PR.

Valid statuses: `proposed`, `accepted`, `superseded`, `deprecated`.

## For plugin-level ADRs

Individual plugins should maintain their own ADRs in `docs/decisions/` within
the plugin directory. This command is for marketplace-wide decisions only. See
the plugin-dev plugin-structure skill for plugin-level ADR guidance.
