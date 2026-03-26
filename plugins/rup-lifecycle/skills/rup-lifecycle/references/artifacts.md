# Artifact Protocol — Detailed Reference

## Status Lifecycle

Every artifact follows this status chain:

```
pending → draft → review → approved
```

- **pending** — Artifact is expected but not yet started
- **draft** — Content exists, still being developed
- **review** — Content is complete, awaiting evaluation
- **approved** — Evaluated and accepted; meets quality standards

Rules:
- Never skip a status (e.g., pending → approved is invalid)
- An approved artifact can return to draft if significant changes are needed (record reason)
- Status is tracked in `.claude/rup-state.json` via the state script

## Bundled File Structure

Artifacts are bundled by phase to reduce file count. Each file contains multiple related sections separated by `## ` headers.

### inception/vision.md

Contains three logical artifacts bundled together:

```markdown
# Product Vision

## Vision Statement
[What the product is, who it's for, why it matters]

## Success Criteria
[Measurable outcomes that define project success]

## Glossary
[Key terms and definitions — shared language for the project]

| Term | Definition |
|------|-----------|
| ... | ... |

## Stakeholder Requests
[Raw stakeholder input, organized by stakeholder]

### [Stakeholder Name/Role]
- Request 1
- Request 2
```

### inception/risk-list.md

Living document that carries across all phases:

```markdown
# Risk List

| ID | Risk | Impact | Probability | Mitigation | Status | Phase Identified |
|----|------|--------|-------------|------------|--------|-----------------|
| R1 | ... | H/M/L | H/M/L | ... | open/mitigated/closed | INC |

## Risk Details

### R1: [Risk Name]
**Impact:** [Detailed impact description]
**Mitigation Strategy:** [What to do about it]
**Contingency:** [What to do if it happens anyway]
**Owner:** [Department]
```

### elaboration/requirements.md

Contains use-case specifications and supplementary (non-functional) requirements:

```markdown
# Requirements

## Use Cases

### UC-01: [Use Case Name]
**Primary Actor:** [Who initiates]
**Preconditions:** [What must be true before]
**Postconditions:** [What must be true after]
**Priority:** [Must/Should/Could]

#### Main Flow
1. ...
2. ...

#### Alternative Flows
- **2a.** [Alternative step]

#### Exceptions
- **3a.** [Error case]

### UC-02: [Next Use Case]
...

## Supplementary Specification

### Performance Requirements
- [Requirement with measurable target]

### Security Requirements
- [Requirement]

### Usability Requirements
- [Requirement]

### Reliability Requirements
- [Requirement]

### Constraints
- [Technical or business constraint]
```

### elaboration/architecture.md

```markdown
# Software Architecture Document

## Architectural Goals and Constraints
[What the architecture optimizes for and why]

## Architectural Representation
[Views used: logical, process, deployment, implementation]

## Logical View
[Components, their responsibilities, and relationships]

## Process View
[Concurrency, synchronization, key workflows]

## Deployment View
[Physical nodes, network topology, deployment mapping]

## Implementation View
[Source organization, layers, key frameworks]

## Key Architectural Decisions

### AD-01: [Decision]
**Context:** [Why this decision was needed]
**Decision:** [What was decided]
**Rationale:** [Why this option over alternatives]
**Consequences:** [Trade-offs accepted]

## Quality Scenarios
[How the architecture satisfies non-functional requirements]
```

### elaboration/dev-plan.md

Bundles the Software Development Plan and Test Strategy:

```markdown
# Development Plan

## Project Overview
[Brief recap of scope and objectives]

## Iteration Plan

### Construction Iterations
| Iteration | Duration | Focus | Key Use Cases |
|-----------|----------|-------|---------------|
| C1 | [weeks] | [theme] | UC-01, UC-02 |
| C2 | [weeks] | [theme] | UC-03, UC-04 |

### Transition Iterations
| Iteration | Duration | Focus |
|-----------|----------|-------|
| T1 | [weeks] | [theme] |

## Resource Allocation
[Department involvement per iteration]

## Risk Management
[Reference to risk-list.md, monitoring approach]

---

# Test Strategy

## Test Levels
- **Unit Testing:** [Approach, coverage targets]
- **Integration Testing:** [Approach, scope]
- **System Testing:** [Approach, environments]
- **Acceptance Testing:** [Approach, who participates]

## Test Environment
[Infrastructure, data, access]

## Quality Criteria
[What "done" looks like for testing]

## Defect Management
[Severity levels, response times, workflow]
```

### construction/build-plan.md

```markdown
# Integration Build Plan

## Build Strategy
[How components are assembled and integrated]

## Build Schedule
| Build | Components | Trigger | Validation |
|-------|-----------|---------|------------|
| B1 | [list] | [when] | [how verified] |

## Integration Order
[Dependency-driven integration sequence]

## Build Verification
[Smoke tests, integration tests per build]
```

### construction/iteration-N/plan.md

```markdown
# Iteration [N] Plan

## Objectives
- [What this iteration achieves]

## Scope
| Item | Type | Priority | Estimate |
|------|------|----------|----------|
| UC-01 implementation | feature | must | [effort] |

## Risks
[Iteration-specific risks from risk-list.md]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
```

### construction/iteration-N/assessment.md

```markdown
# Iteration [N] Assessment

## Summary
[What was accomplished vs. planned]

## Results
| Item | Status | Notes |
|------|--------|-------|
| UC-01 | complete | [notes] |

## Quality Metrics
- Test coverage: [%]
- Defects found: [count]
- Defects resolved: [count]

## Lessons Learned
- [What worked]
- [What to improve]

## Impact on Plan
[Adjustments needed for remaining iterations]
```

### transition/release.md

Bundles Deployment Plan and Release Notes:

```markdown
# Deployment Plan

## Deployment Strategy
[Blue-green, canary, big bang, etc.]

## Pre-Deployment Checklist
- [ ] All acceptance tests pass
- [ ] Performance benchmarks met
- [ ] Security scan clean
- [ ] Rollback procedure tested

## Deployment Steps
1. [Step-by-step deployment procedure]

## Rollback Procedure
1. [Step-by-step rollback if needed]

## Post-Deployment Verification
- [ ] [Health check 1]
- [ ] [Health check 2]

---

# Release Notes

## Version [X.Y.Z] — [Date]

### New Features
- [Feature from UC-01]

### Improvements
- [Enhancement]

### Bug Fixes
- [Fix]

### Known Issues
- [Issue with workaround]

### Breaking Changes
- [Change requiring user action]
```
