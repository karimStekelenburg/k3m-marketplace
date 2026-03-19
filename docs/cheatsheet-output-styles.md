# Output Style .md — Complete Frontmatter Reference

Location: `<plugin-root>/output-styles/<style-name>.md`

Output styles modify Claude's response behavior for the duration of a session. They're applied via hooks (typically SessionStart) that inject style instructions into Claude's context.

## Frontmatter Fields

### name
- **Type:** `string`
- **Format:** kebab-case identifier
- **Example:** `name: explanatory`

### description
- **Type:** `string`
- **Purpose:** Describes what this output style does
- **Example:** `description: Adds educational insights about implementation choices`

### version
- **Type:** `string` (semver)
- **Example:** `version: 1.0.0`

### keep-coding-instructions
- **Type:** `boolean`
- **Default:** `false`
- **Purpose:** When `true`, preserves Claude Code's default coding instructions alongside the style
- **Example:** `keep-coding-instructions: true`

## How Output Styles Work

Output styles are NOT a built-in component type like commands or skills. They're a **convention** implemented through hooks:

1. Define the style as a markdown file with instructions
2. Use a SessionStart hook to inject the style instructions
3. The hook reads the style file and returns it as a `systemMessage`

## Implementation Pattern

### Style definition (`output-styles/explanatory.md`)

```markdown
---
name: explanatory
description: Adds educational context to responses
version: 1.0.0
---

When responding, add educational insights:

1. After each code change, explain WHY this approach was chosen
2. Note alternative approaches considered and trade-offs
3. Connect changes to broader patterns and principles
4. Highlight non-obvious implications
```

### Hook to apply it (`hooks/hooks.json`)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/apply-style.sh"
          }
        ]
      }
    ]
  }
}
```

### Hook script (`hooks/apply-style.sh`)

```bash
#!/bin/bash
STYLE_FILE="${CLAUDE_PLUGIN_ROOT}/output-styles/explanatory.md"
if [ -f "$STYLE_FILE" ]; then
  # Extract content after frontmatter
  CONTENT=$(awk '/^---$/{i++; next} i>=2' "$STYLE_FILE")
  echo "{\"systemMessage\": $(echo "$CONTENT" | jq -Rs .)}"
fi
```

## Gotchas

1. **Not a built-in component type** — output styles are a convention, not auto-discovered
2. **Requires hooks** to inject into Claude's context
3. **SessionStart is typical hook event** — applies style at session begin
4. **Style persists for session** — can't be changed without restart
5. **Keep styles focused** — overly broad styles degrade response quality
6. **Plugin can declare `outputStyles` path** in plugin.json for organization

## Complete Example

```markdown
---
name: concise
description: Minimal, direct responses with no preamble
version: 1.0.0
---

Response guidelines:
- Lead with the answer, not the reasoning
- Skip filler words and transitions
- No summaries at end of responses
- Code over prose when possible
- One sentence where others would use three
```
