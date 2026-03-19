# AGENT.md — Complete Frontmatter Reference

Location: `<plugin-root>/agents/<agent-name>.md`

Agents are autonomous subprocesses that handle complex, multi-step tasks independently. Claude spawns them via the Agent tool when the description matches the current task.

## Frontmatter Fields

### name (required)
- **Type:** `string`
- **Format:** lowercase, numbers, hyphens only; 3-50 chars; must start/end with alphanumeric
- **Example:** `name: code-reviewer`

### description (required)
- **Type:** `string`
- **Purpose:** Defines when Claude should trigger this agent — most critical field
- **Must include:** Triggering conditions + `<example>` blocks
- **Example:**
  ```yaml
  description: >-
    Use this agent when the user asks for a thorough code review, security audit,
    or quality analysis of code changes. Examples:

    <example>
    Context: User just finished implementing a feature
    user: "Review my changes before I create a PR"
    assistant: "I'll launch the code-reviewer agent to analyze your changes."
    <commentary>
    User wants pre-PR review — this agent specializes in thorough code analysis.
    </commentary>
    </example>
  ```

### model (required)
- **Type:** `string`
- **Options:** `inherit`, `sonnet`, `opus`, `haiku`
- **Recommendation:** Use `inherit` unless the agent needs specific capabilities
- **Example:** `model: inherit`

### color (required)
- **Type:** `string`
- **Options:** `blue`, `cyan`, `green`, `yellow`, `magenta`, `red`
- **Guidelines:**
  - Blue/cyan: Analysis, review
  - Green: Success-oriented tasks
  - Yellow: Caution, validation
  - Red: Critical, security
  - Magenta: Creative, generation

### tools (optional)
- **Type:** `string[]`
- **Default:** All tools available if omitted
- **Purpose:** Restrict agent to specific tools (principle of least privilege)
- **Common sets:**
  - Read-only: `["Read", "Grep", "Glob"]`
  - Code generation: `["Read", "Write", "Grep"]`
  - Testing: `["Read", "Bash", "Grep"]`
- **Example:** `tools: ["Read", "Write", "Grep", "Bash"]`

## Body Content

The markdown body becomes the agent's system prompt. Write in second person.

**Standard structure:**
```markdown
You are [role] specializing in [domain].

**Your Core Responsibilities:**
1. [Primary responsibility]
2. [Secondary responsibility]

**Analysis Process:**
1. [Step one]
2. [Step two]

**Output Format:**
[What the agent should return]

**Edge Cases:**
- [Case]: [How to handle]
```

## Gotchas

1. **All four frontmatter fields are required** — name, description, model, color
2. **Description MUST include `<example>` blocks** — these teach Claude when to spawn the agent
3. **Include 2-4 examples** covering different triggering scenarios
4. **System prompt in second person** — "You are...", "You will..."
5. **Keep system prompt under 10,000 characters**
6. **Agent names are auto-namespaced** by plugin

## Complete Example

```markdown
---
name: security-analyzer
description: >-
  Use this agent when code needs security review, the user mentions
  "security audit", "vulnerability check", or when editing authentication,
  authorization, or data handling code. Examples:

  <example>
  Context: User is working on authentication code
  user: "Check this auth implementation for vulnerabilities"
  assistant: "I'll launch the security-analyzer agent for a thorough security review."
  <commentary>
  Auth code requires specialized security analysis — this agent has the expertise.
  </commentary>
  </example>

  <example>
  Context: User finished a feature touching user data
  user: "Can you audit the data handling in this PR?"
  assistant: "Launching security-analyzer to audit data handling patterns."
  <commentary>
  Data handling code benefits from security-focused review.
  </commentary>
  </example>
model: inherit
color: red
tools: ["Read", "Grep", "Glob"]
---

You are a security analysis expert specializing in application security.

**Your Core Responsibilities:**
1. Identify OWASP Top 10 vulnerabilities
2. Check authentication and authorization patterns
3. Validate input sanitization and output encoding
4. Review cryptographic usage

**Analysis Process:**
1. Read all changed files
2. Identify security-sensitive code paths
3. Check for common vulnerability patterns
4. Assess severity and exploitability

**Output Format:**
For each finding:
- **Severity:** Critical/High/Medium/Low
- **Location:** file:line
- **Issue:** Description
- **Fix:** Recommended remediation
```
