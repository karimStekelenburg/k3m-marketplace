---
name: spec
description: Generate a technical specification from a roadmap milestone. Reads the roadmap, design doc, and existing specs to produce a detailed spec for the next milestone.
---

# Spec Writer

Generate a technical specification for a roadmap milestone.

## Inputs

The user provides a milestone identifier (e.g., "v0.2", "Canvas Viewport") or asks for "the next spec."

## Backend

Detect backend and source it:
```
source "$CLAUDE_PLUGIN_ROOT/scripts/detect-backend.sh" && source "$K3M_BACKEND_SCRIPT"
```

## Workflow

1. **Read context:**
   - Roadmap: `k3m_read_roadmap` — find the target milestone
   - `docs/DESIGN.md` — architectural context (always on filesystem)
   - Existing specs: check `docs/specs/` (fs) or marked comments (github)
   - `src/` — current implementation

2. **Generate the spec** with this structure:

```markdown
# v{X.Y.0} — {Milestone Name}: Technical Spec

> **Status:** Draft · **Date:** {today}
> **Depends on:** {previous milestone}
> **Estimated effort:** {from roadmap}

---

## 1. Goal
## 2. Design decisions
## 3. Architecture
### 3.1 Class structure
### 3.2 File layout
## 4. Data model
## 5. Public API
## 6. Internal implementation
## 7. Event flow
## 8. Acceptance criteria
## 9. Playground update
## 10. Migration / breaking changes
## 11. Open questions
```

3. **Write the spec:**
   - **fs:** Write to `docs/specs/v{X.Y}-{kebab-case-name}.md`
   - **github:** Post as marked comment (`<!-- k3m:spec -->`) on the milestone issue

4. **Update state:**
   - **fs:** File existence is the state
   - **github:** Add `specced` label to the issue

5. **Report** the file path/location and a brief summary.

## Guidelines

- Be concrete: include actual TypeScript signatures, not vague descriptions
- Reference existing code by file path when describing what changes
- Each acceptance criterion must be binary pass/fail — no subjective language
- Keep the spec self-contained
