# Import Process Checklist

Use this checklist to verify a codebase import is CMMI-compliant.
Check each item as you complete it.

## Phase 1 — Retro-Specification

### L5 Unit Level
- [ ] All complex functions identified (>10 lines, branching, I/O)
- [ ] Unit contract written for each complex function
- [ ] Pre/post-conditions documented
- [ ] Error handling documented
- [ ] Algorithm sketch included
- [ ] LLD document ID assigned

### L4 Module Level
- [ ] All modules (source files) identified
- [ ] Module spec written for each
- [ ] Public API documented with signatures and types
- [ ] Internal coordination (call graph) documented
- [ ] Class diagram (PlantUML) created
- [ ] MLD document ID assigned

### L3 Component Level
- [ ] All components (packages/services) identified
- [ ] Component spec written for each
- [ ] Component contract and interface documented
- [ ] Module decomposition documented
- [ ] Component diagram (PlantUML) created
- [ ] HLD document ID assigned
- [ ] RACI matrix created

### L2 System Level
- [ ] System architecture documented
- [ ] External interfaces documented
- [ ] Data flow documented
- [ ] Non-functional requirements documented
- [ ] Sequence diagram (PlantUML) created
- [ ] Deployment diagram (PlantUML) created
- [ ] SRS/SAD document ID assigned
- [ ] RACI matrix created

### L1 Business Level
- [ ] Business goal documented
- [ ] Stakeholders identified
- [ ] Use cases documented with acceptance criteria
- [ ] Domain model documented
- [ ] Use case diagram (PlantUML) created
- [ ] BRD document ID assigned
- [ ] RACI matrix created

### Cross-Cutting
- [ ] Traceability matrix: every L5 unit traces up to L4 module
- [ ] Traceability matrix: every L4 module traces up to L3 component
- [ ] Traceability matrix: every L3 component traces up to L2 system
- [ ] Traceability matrix: every L2 system traces up to L1 business

## Phase 2 — Test Plan Design

- [ ] AT-NNN acceptance test cases designed (L1)
- [ ] ST-NNN system test cases designed (L2)
- [ ] CT-NNN component test cases designed (L3)
- [ ] MT-NNN module test cases designed (L4)
- [ ] UT-NNN unit test cases designed (L5)
- [ ] Every test case traces to a specification requirement

## Phase 3 — Test Implementation & Execution

- [ ] Unit tests implemented and passing
- [ ] Module tests implemented and passing
- [ ] Component tests implemented and passing
- [ ] System tests implemented and passing
- [ ] Acceptance tests implemented and passing
- [ ] `pyproject.toml` or equivalent created with test dependencies
- [ ] Test runner command documented

## Phase 4 — Compliance Artifacts

- [ ] SQA summary report generated
- [ ] Metrics collected per `cmmi-metrics-collection`
- [ ] Communication log entries created per `communication`
- [ ] All artifacts committed to version control
- [ ] Coherency audit run (`cmmi-coherency-audit`)
