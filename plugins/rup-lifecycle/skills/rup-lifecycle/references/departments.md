# Department × Phase Task Matrix

This matrix defines what each department is responsible for in each phase. Use it to determine what work needs to happen and who owns it.

## Product Management (PM)

### Inception
- Conduct stakeholder interviews
- Draft product vision and success criteria
- Define project scope boundaries
- Create initial use-case briefs
- Build project glossary
- Estimate high-level cost and timeline

### Elaboration
- Refine and complete use-case specifications
- Write supplementary specifications (non-functional requirements)
- Manage scope — push back on feature creep
- Create development plan with iteration breakdown
- Prioritize use cases for Construction iterations

### Construction
- Track iteration progress against plan
- Manage change requests and scope adjustments
- Communicate status to stakeholders
- Review iteration assessments
- Coordinate user feedback on intermediate builds

### Transition
- Coordinate user acceptance testing
- Draft release communication
- Obtain stakeholder sign-off
- Plan post-release support
- Conduct lessons-learned review

---

## Solutions Architecture (SA)

### Inception
- Assess technical feasibility
- Evaluate technology options
- Identify architectural risks
- Provide rough effort estimates for PM

### Elaboration
- Design software architecture (components, interfaces, data model)
- Build executable architectural prototype
- Validate architecture against non-functional requirements
- Document key architectural decisions and rationale
- Identify reusable components and frameworks

### Construction
- Guide implementation of complex features
- Review code for architectural compliance
- Resolve design questions that arise during implementation
- Update architecture documentation for deviations

### Transition
- Review final architecture against original vision
- Assess technical debt accumulated during Construction
- Document architecture for maintenance teams
- Validate deployment architecture

---

## Engineering (ENG)

### Inception
- Build proof-of-concept for high-risk technical elements (if requested)
- Provide technical input on feasibility

### Elaboration
- Implement architectural prototype
- Set up project structure, build system, and tooling
- Implement risk-mitigation spikes
- Establish coding standards and patterns

### Construction
- Implement features according to iteration plans
- Write unit tests and integration tests
- Perform code reviews
- Fix defects from QA testing
- Maintain code quality and test coverage

### Transition
- Fix critical and high-priority bugs
- Optimize performance bottlenecks
- Support deployment process
- Implement monitoring and alerting hooks

---

## Quality Assurance (QA)

### Inception
- Review use cases for testability
- Identify quality risks

### Elaboration
- Define test strategy (what, when, how)
- Design test architecture (frameworks, environments)
- Plan test data management
- Create initial test cases for architectural prototype

### Construction
- Execute integration tests each iteration
- Run regression test suites
- Track and report defects
- Validate fixes
- Assess iteration quality in assessments

### Transition
- Execute acceptance tests
- Perform performance and security testing
- Validate deployment procedures
- Sign off on release quality

---

## DevOps (OPS)

### Inception
- Identify deployment environment requirements
- Flag infrastructure constraints or risks

### Elaboration
- Design CI/CD pipeline architecture
- Set up development and staging environments
- Plan monitoring and observability
- Design deployment strategy (blue-green, canary, etc.)

### Construction
- Maintain CI/CD pipeline
- Manage staging environments
- Set up monitoring and alerting
- Prepare production infrastructure
- Create deployment automation

### Transition
- Execute deployment to production
- Monitor post-deployment health
- Manage rollback procedures
- Hand off operational documentation
- Validate monitoring and alerting in production
