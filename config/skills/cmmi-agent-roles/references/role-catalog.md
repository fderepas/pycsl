# Role Catalog — CMMI Governance and V-Cycle Engineering Roles

This reference defines the organizational roles available for agent persona
assignment. Roles are split into two layers: Governance (CMMI process oversight)
and Engineering (V-Cycle product execution). Each role includes selection
criteria, specification-level alignment, and primary responsibilities.

## How to Use This File

1. Identify which specification levels (1–5) the project covers.
2. Select Engineering roles for each in-scope level using the selection criteria.
3. Select Governance roles based on the target CMMI maturity level.
4. Use the Role-to-Level Mapping Table (§3) to validate complete coverage.

---

## 1. CMMI Governance Roles (Process Oversight Layer)

These roles are cross-cutting. They do not produce product features; they
ensure that the processes used to build those features are standardized,
measured, and auditable.

### 1.1 EPG / SEPG Member

| Field | Value |
|---|---|
| Full Title | Engineering Process Group / Software Engineering Process Group Member |
| Layer | Governance |
| Level Alignment | Cross-cutting (all levels) |
| CMMI Practice Area | Organizational Process Definition (OPD) |

**Primary Responsibilities:**

- Define and maintain organizational standard operating procedures.
- Create and manage document templates for all 5 specification levels.
- Maintain the Organizational Process Asset Library (OPAL).
- Facilitate process improvement initiatives.

**Selection Criteria — include this role when:**

- [ ] The project targets CMMI Level 2 or higher.
- [ ] The organization requires standardized document templates.
- [ ] Multiple projects share a common process framework.

**Selection Criteria — may exclude this role when:**

- [ ] The project is a single, small-scale effort with no process standardization requirement.

---

### 1.2 Configuration Manager (CM)

| Field | Value |
|---|---|
| Full Title | Configuration Manager |
| Layer | Governance |
| Level Alignment | Cross-cutting (all levels, with emphasis on Levels 1–2 baselining) |
| CMMI Practice Area | Configuration Management (CM) |

**Primary Responsibilities:**

- Control central repositories for code and documentation.
- Manage version control and execute baseline audits.
- Facilitate the Change Control Board (CCB) for specification changes at any level.
- Manage API versioning and documentation baselines (Level 3).

**Selection Criteria — include this role when:**

- [ ] The project has version-controlled documentation or code.
- [ ] Change control is required for specifications at any level.
- [ ] The project targets CMMI Level 2 or higher.

**Selection Criteria — may exclude this role when:**

- [ ] The project has no formal version control or baselining requirements.

---

### 1.3 SQA Auditor

| Field | Value |
|---|---|
| Full Title | Software Quality Assurance Auditor |
| Layer | Governance |
| Level Alignment | Cross-cutting (all levels) |
| CMMI Practice Area | Process Quality Assurance (PQA) |

**Primary Responsibilities:**

- Verify that the team follows defined processes at each specification level.
- Confirm that design documents are peer-reviewed before downstream work begins.
- Audit system design review records (Level 2).
- Check code-review participation rates (Levels 4–5).
- Report non-compliance findings to management.

**Selection Criteria — include this role when:**

- [ ] The project requires objective process compliance verification.
- [ ] CMMI appraisal evidence must demonstrate process adherence.
- [ ] The project targets CMMI Level 2 or higher.

**Selection Criteria — may exclude this role when:**

- [ ] The project has no formal quality assurance requirements.

---

### 1.4 Metrics Analyst

| Field | Value |
|---|---|
| Full Title | Measurement / Metrics Analyst |
| Layer | Governance |
| Level Alignment | Cross-cutting (all levels, with emphasis on Levels 4–5 metrics) |
| CMMI Practice Area | Managing Performance and Measurement (MPM) |

**Primary Responsibilities:**

- Collect metrics across all specification levels (requirements churn at Level 1, defect density at Level 4).
- Analyze process performance and identify bottlenecks.
- Collect static analysis and unit test coverage metrics (Level 5).
- Report aggregated metrics at governance review cycles.

**Selection Criteria — include this role when:**

- [ ] The project requires quantitative process measurement.
- [ ] The project targets CMMI Level 3 or higher.
- [ ] Process performance baselines are needed.

**Selection Criteria — may exclude this role when:**

- [ ] The project targets CMMI Level 2 with minimal measurement requirements.
- [ ] Metrics collection is handled by existing tooling without a dedicated role.

---

## 2. V-Cycle Engineering Roles (Product Execution Layer)

These roles align directly with the top-down specification and bottom-up
verification phases of the product lifecycle.

### 2.1 Business Analyst / Product Owner

| Field | Value |
|---|---|
| Full Title | Business Analyst (BA) / Product Owner (PO) |
| Layer | Engineering |
| Level Alignment | Level 1 — Business |
| Specification Focus | Business goals, user workflows, domain models |

**Primary Responsibilities:**

- Translate real-world operational problems into structured business requirements.
- Write User Stories, Use Cases, and Business Requirements Documents (BRDs).
- Define acceptance criteria for User Acceptance Testing (UAT).
- Conduct stakeholder interviews, workshops, and market analysis.

**Selection Criteria — include this role when:**

- [ ] Specification Level 1 (Business) is in scope.

---

### 2.2 System Architect / Systems Engineer

| Field | Value |
|---|---|
| Full Title | System Architect / Systems Engineer |
| Layer | Engineering |
| Level Alignment | Level 2 — System |
| Specification Focus | Architecture, subsystem decomposition, interfaces |

**Primary Responsibilities:**

- Bridge business needs and technical capabilities.
- Decompose requirements into systems and subsystems.
- Write the System Requirements Specification (SRS) and Interface Control Document (ICD).
- Define technology stacks and inter-system communication protocols.

**Selection Criteria — include this role when:**

- [ ] Specification Level 2 (System) is in scope.
- [ ] The project involves multiple subsystems or services.

---

### 2.3 Technical Lead / Component Architect

| Field | Value |
|---|---|
| Full Title | Technical Lead / Component Architect |
| Layer | Engineering |
| Level Alignment | Level 3 — Component (Library / Package / Service) |
| Specification Focus | Components (libraries, crates, packages, services), design patterns, API contracts |

**Primary Responsibilities:**

- Take system allocations and decompose them into components such as libraries, packages, and services.
- Select design patterns suited to the problem (Factory, Strategy, MVC).
- Generate UML component, class, and sequence diagrams.
- Define API / contract specifications (OpenAPI/Swagger, gRPC .proto).

**Selection Criteria — include this role when:**

- [ ] Specification Level 3 (Component) is in scope.

---

### 2.4 Software Engineer (Developer)

| Field | Value |
|---|---|
| Full Title | Software Engineer / Developer |
| Layer | Engineering |
| Level Alignment | Level 4 — Module / Level 5 — Unit |
| Specification Focus | Modules (classes, internal interfaces, state management) and Units (functions, algorithms, error handling) |

**Primary Responsibilities:**

- Decompose components into classes and modules with clear internal responsibilities.
- Define internal interfaces, state management, and calling conventions between units.
- Write Module-Level Design (MLD) artifacts and unit-level pseudo-code where needed.
- Transform module designs and algorithmic rules into source code.
- Write inline code documentation (Javadoc, JSDoc, Doxygen).
- Define explicit boundary conditions, input/output contracts, and exception handling.

**Selection Criteria — include this role when:**

- [ ] Specification Level 4 (Module) or Level 5 (Unit) is in scope.

---

### 2.5 Test Engineer (QA)

| Field | Value |
|---|---|
| Full Title | Test Engineer / Quality Assurance Engineer |
| Layer | Engineering |
| Level Alignment | All levels (specialization varies by level) |
| Specification Focus | Verification and validation across the V-Cycle |

**Primary Responsibilities by Level:**

| Level | Test Specialization | Responsibility |
|---|---|---|
| Level 1 | UAT Test Engineer | Execute User Acceptance Testing with real-world scenarios |
| Level 2 | System Test Engineer | Perform end-to-end system testing, regression, performance, and security validation |
| Level 3 | Integration Test Engineer | Verify component communication, data contract adherence, component assembly |
| Level 4 | Module Test Engineer | Test module internals: class interactions, state management, internal interfaces |
| Level 5 | Unit Test Engineer / Peer Reviewer | Execute peer code reviews, run automated unit test suites (JUnit, PyTest) |

**Selection Criteria — include this role when:**

- [ ] Any specification level is in scope (at least one test specialization is needed).

**Persona generation note:** For projects covering 3+ levels, generate separate
test engineer personas per level. For projects covering 1–2 levels, a single
multi-level test engineer persona is acceptable (see Tailoring Guidelines in SKILL.md §6).

---

### 2.6 Reconciliator

| Field | Value |
|---|---|
| Full Title | Reconciliator (alias: Reconciliation Agent) |
| Layer | Engineering |
| Level Alignment | All levels (cross-cutting) |
| Specification Focus | Fault attribution on test failure, re-work loop management |
| CMMI Practice Area | Process Quality Assurance (PQA) |

**Primary Responsibilities:**

- Analyze test failures at any specification level to determine the responsible party.
- Classify the root cause as one of three fault types:
  - **Specifier fault**: the specification is impossible, incomplete, or the
    decomposition/coordination of sub-level actors is wrong — even if all
    sub-actors performed correctly.
  - **Verifier fault**: the test plan itself contains errors (wrong expected
    values, incorrect test logic, missing preconditions).
  - **Level-below fault**: one or more actors at the level below did not
    deliver results conforming to their specifications.
- Trigger re-work by routing the failure back to the responsible party.
- Maintain a reconciliation log recording each failure, fault classification,
  and re-work action taken.
- Escalate to the governance layer (SQA / EPG) when the same level fails
  reconciliation 3 times consecutively without resolution.

**Selection Criteria — include this role when:**

- [ ] Any specification level includes both a Specifier and a Verifier.
- [ ] The project uses the recursive level-based execution model.

**Selection Criteria — may exclude this role when:**

- [ ] The project targets only a single specification level with no
  sub-level delegation (e.g., Profile S with direct code development).

---

## 3. Role-to-Level Mapping Table

| Specification Level | Primary Specifier (Engineering) | CMMI Governance | Verifier (Engineering) | Reconciliation (Engineering) |
|---|---|---|---|---|
| **1. Business** | Business Analyst / Product Owner | CM (baselines requirements scope), EPG (provides templates) | UAT Test Engineer | Reconciliator |
| **2. System** | System Architect / Systems Engineer | CCB (evaluates change impact), SQA (audits design reviews) | System Test Engineer | Reconciliator |
| **3. Component** | Technical Lead / Component Architect | CM (manages API versioning and doc baselines) | Integration Test Engineer | Reconciliator |
| **4. Module** | Software Engineer | SQA (checks review rates), Metrics Analyst (collects module metrics) | Module Test Engineer | Reconciliator |
| **5. Unit** | Software Engineer | Metrics Analyst (collects coverage metrics), SQA (checks review rates) | Unit Test Engineer / Peer Reviewer | Reconciliator |

## 4. Coverage Validation Rule

A valid role assignment must satisfy all of the following:

- [ ] Every in-scope specification level has exactly one Primary Specifier assigned.
- [ ] Every in-scope specification level has at least one Governance role assigned.
- [ ] Every in-scope specification level has at least one Verifier assigned.
- [ ] Every in-scope specification level that uses recursive level-based execution has a Reconciliation role assigned.
- [ ] All Governance roles required by the target CMMI maturity level are assigned.
- [ ] No role is assigned without a corresponding in-scope specification level (no orphan roles).
