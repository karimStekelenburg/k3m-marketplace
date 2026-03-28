---
description: Update a plugin's reference documentation by fetching current content from indexed sources, comparing semantically, and proposing changes. Use after check-staleness identifies outdated references.
---

# Update References

Fetch current documentation from indexed sources, compare against existing reference material, and propose updates. All changes are presented for review before being applied (NF3).

## Input

$ARGUMENTS can be:
- A plugin name (e.g., `plugin-dev`) — updates that plugin's references
- A specific source ID (e.g., `plugin-dev:hooks-reference`) — updates one source
- `shared` — updates the shared reference documentation
- `all` — updates everything

## Process

### Step 1: Identify sources to update

Read the relevant `index.yaml` file(s) and identify sources that need updating:
- Sources flagged by `/marketplace-maintenance:check-staleness`
- Sources with `last_fetched: null`
- Sources explicitly requested

### Step 2: Fetch current documentation

For each source to update:

1. **Try the stored URL first.** Fetch the URL from the source's `url` field.

2. **Handle URL breakage.** If the URL returns no useful content (404, unrelated redirect, empty page):
   - Fetch the documentation index (`llms.txt` from `changelog_sources`)
   - Search the index for the topic described in the source's `description` field
   - If a matching page is found, update the `url` field and fetch from the new URL
   - If no match found, report the breakage and skip this source

3. **Extract relevant content.** From the fetched page, extract the content relevant to the source's `description` and `coverage_notes`.

### Step 3: Semantic comparison

Compare the fetched content against the existing `local_doc` file:

**If local_doc doesn't exist (first fetch):**
- Condense the fetched content into a reference document
- Focus on information that would be non-obvious to Claude
- Preserve key details: field names, valid values, configuration formats, event types
- Target 2,000-4,000 words for comprehensive references

**If local_doc exists (update):**
- Identify **additions**: new features, events, fields, or capabilities not in the local doc
- Identify **removals**: deprecated or removed features still documented locally
- Identify **contradictions**: information that conflicts between local and current
- Identify **unchanged**: content that is still accurate

### Step 4: Propose changes

Present the comparison results for review:

```
## Update Proposal: {source-id}

### Source: {url}
### Current local doc: {local_doc path}

### Additions (new content to add)
- [List specific additions with context]

### Removals (outdated content to remove)
- [List specific removals with context]

### Contradictions (content to correct)
- [List contradictions with what's wrong and what's right]

### Unchanged (confirmed current)
- [Brief summary of what's still accurate]

### Proposed action
Apply these changes to {local_doc}? [Present the updated content]
```

### Step 5: Apply changes (with approval)

Only proceed when the user explicitly approves. Then:

1. Update the `local_doc` file with the proposed changes
2. Update the source's `last_fetched` timestamp in `index.yaml`
3. Update `coverage_notes` in `index.yaml` if the scope of the document changed
4. Update the `last_verified` timestamp at the index level

### Step 6: Update plugin skills if needed

If the reference docs inform a plugin's skills (e.g., hook event list in hook-development SKILL.md):
- Identify which SKILL.md files reference the updated content
- Propose updates to those SKILL.md files as well
- Never auto-apply — present for review

## Error handling

- **Network failures:** Report clearly and skip the source. Don't fail the entire batch.
- **Parse failures:** If fetched content can't be meaningfully parsed, report and skip.
- **Ambiguous changes:** When it's unclear whether something was intentionally omitted from the local doc vs. missing, flag it as "possible addition" and let the user decide.

## Key principles

1. **Never auto-apply.** All changes are proposals until explicitly approved.
2. **Preserve intentional condensation.** Local docs are deliberately condensed versions. New information should be added, but the condensation style should be preserved.
3. **Handle URL breakage gracefully.** URLs change. Always fall back to search rather than failing.
4. **Update timestamps accurately.** Only update `last_fetched` after content is actually reviewed and updated.
