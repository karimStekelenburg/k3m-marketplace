# RUP Phases — Detailed Reference

## Phase 1: Inception (INC)

### Objective
Establish the business case and scope. Understand what to build, for whom, and why. Identify key risks early. Achieve stakeholder agreement on vision and scope.

### Key Activities
- Define product vision and success criteria
- Identify key stakeholders and their needs
- Create initial use cases (10-20% detail)
- Perform initial risk assessment
- Establish project glossary
- Estimate cost and schedule at high level

### Primary Departments
- **PM**: Owns vision, stakeholder interviews, scope definition
- **SA**: Initial feasibility assessment, technology evaluation
- **ENG**: Proof-of-concept for high-risk technical elements (if needed)
- **QA**: Initial test strategy thinking
- **OPS**: Deployment environment considerations

### Required Artifacts (Exit Criteria)
| Artifact | Required Status | Notes |
|----------|----------------|-------|
| vision.md | approved | Must include Vision, Glossary, and Stakeholder Requests sections |
| risk-list.md | draft | Initial identification; will evolve through all phases |

### Iteration Pattern
- **initial cycle**: 1-2 iterations. Thorough exploration.
- **evolution cycle**: 1 iteration. Quick delta assessment — what changed since last cycle.
- **maintenance cycle**: 0-1 iterations. May skip directly to Elaboration if scope is obvious.

### Gate: Lifecycle Objectives Milestone
To pass, demonstrate:
1. All stakeholders agree on scope and vision
2. Key risks identified (even if not yet mitigated)
3. Initial use cases capture the core functionality
4. Cost/schedule estimate is credible (order of magnitude)

---

## Phase 2: Elaboration (ELB)

### Objective
Establish the architecture baseline. Mitigate the highest risks. Fully specify requirements. Create a credible development plan.

### Key Activities
- Detail all use cases and supplementary specs
- Design and validate the software architecture
- Build architectural prototype (executable architecture)
- Mitigate critical risks through prototyping/investigation
- Create detailed development plan with iterations
- Define test strategy

### Primary Departments
- **SA**: Architecture design, prototyping, technology decisions
- **PM**: Requirements refinement, scope management, planning
- **ENG**: Architectural prototype, risk mitigation code
- **QA**: Test strategy, test environment planning
- **OPS**: Infrastructure architecture, CI/CD pipeline design

### Required Artifacts (Exit Criteria)
| Artifact | Required Status | Notes |
|----------|----------------|-------|
| vision.md | approved | Refined from Inception |
| requirements.md | approved | Complete Use-Case Specs + Supplementary Spec |
| architecture.md | approved | Validated through executable prototype |
| dev-plan.md | approved | Includes iteration plan + test strategy |
| risk-list.md | approved | All critical risks have mitigation plans |

### Iteration Pattern
- **initial cycle**: 2-3 iterations. Architecture exploration and validation.
- **evolution cycle**: 1-2 iterations. Delta architecture for new features.
- **maintenance cycle**: 1 iteration. Confirm fix approach doesn't break architecture.

### Gate: Lifecycle Architecture Milestone
To pass, demonstrate:
1. Architecture is stable and validated (prototype exists)
2. All critical risks mitigated or have mitigation plans
3. Requirements are complete enough to plan Construction
4. Development plan has credible iteration breakdown
5. All stakeholders agree on the plan

---

## Phase 3: Construction (CON)

### Objective
Build the product. Implement all remaining use cases on the architectural baseline. Achieve beta quality.

### Key Activities
- Implement features iteration by iteration
- Continuous integration and testing
- Write iteration plans and assessments
- Manage defects and change requests
- Prepare deployment infrastructure

### Primary Departments
- **ENG**: Implementation, code reviews, unit testing
- **QA**: Integration testing, regression testing, defect tracking
- **OPS**: CI/CD pipeline, staging environment, monitoring
- **SA**: Architecture guidance, design decisions for complex features
- **PM**: Iteration tracking, scope management, stakeholder communication

### Required Artifacts (Exit Criteria)
| Artifact | Required Status | Notes |
|----------|----------------|-------|
| build-plan.md | approved | Integration build plan for assembling components |
| iteration-N/plan.md | exists | One per iteration |
| iteration-N/assessment.md | exists | At least one completed iteration assessment |

### Iteration Pattern
- **initial cycle**: 3-6 iterations. Full implementation.
- **evolution cycle**: 2-4 iterations. Feature additions.
- **maintenance cycle**: 1-2 iterations. Targeted fixes.

### Gate: Initial Operational Capability Milestone
To pass, demonstrate:
1. Product is feature-complete (beta quality)
2. All iteration assessments show acceptable quality
3. Deployment plan exists and is validated
4. User documentation sufficient for beta testing

---

## Phase 4: Transition (TRN)

### Objective
Deliver the product to users. Achieve production quality. Ensure smooth deployment and handoff.

### Key Activities
- Final testing (acceptance, performance, security)
- User acceptance testing coordination
- Deployment execution
- Release documentation
- Knowledge transfer
- Post-deployment monitoring

### Primary Departments
- **OPS**: Deployment execution, monitoring, rollback planning
- **QA**: Final acceptance testing, performance validation
- **ENG**: Critical bug fixes, performance optimization
- **PM**: Release communication, stakeholder sign-off
- **SA**: Architecture review, technical debt assessment

### Required Artifacts (Exit Criteria)
| Artifact | Required Status | Notes |
|----------|----------------|-------|
| release.md | approved | Deployment Plan + Release Notes |

### Iteration Pattern
- **initial cycle**: 1-2 iterations. Full deployment process.
- **evolution cycle**: 1 iteration. Incremental release.
- **maintenance cycle**: 1 iteration. Patch release.

### Gate: Product Release Milestone
To pass, demonstrate:
1. All acceptance criteria met
2. Deployment successful (or validated in staging)
3. Release notes document all changes
4. Stakeholder sign-off obtained
