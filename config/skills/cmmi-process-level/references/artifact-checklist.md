# Per-Level Artifact Checklist

Use this checklist to audit documentation coverage at each specification level.
For each artifact, mark **Present**, **Partial**, or **Missing**. An artifact is:

- **Present:** The artifact exists, is current, and contains all required sections.
- **Partial:** The artifact exists but is incomplete, outdated, or missing key sections.
- **Missing:** The artifact does not exist.

---

## Level 1 — Business

| # | Artifact | Required | Status | Notes |
|---|---|---|---|---|
| 1.1 | Business Requirements Document (BRD) or Product Vision | Yes | ☐ Present ☐ Partial ☐ Missing | Must state commercial/operational goals |
| 1.2 | User Stories / Epic Specifications with Acceptance Criteria | Yes | ☐ Present ☐ Partial ☐ Missing | Must use "As a… I want to… So that…" format with explicit acceptance criteria |
| 1.3 | Use Case Blueprints | Yes | ☐ Present ☐ Partial ☐ Missing | Step-by-step actor-system interaction narratives |
| 1.4 | Domain Model | Recommended | ☐ Present ☐ Partial ☐ Missing | Business entities and real-world interactions, technology-independent |
| 1.5 | UAT Plan / Test Scenarios | Yes | ☐ Present ☐ Partial ☐ Missing | Real-life scenarios executed by end-users |

### Level 1 Gap Severity Rules

| Condition | Severity |
|---|---|
| BRD/Product Vision is Missing | Critical |
| User Stories exist but lack Acceptance Criteria | Major |
| Use Case Blueprints are Missing | Major |
| UAT Plan is Missing | Major |
| Domain Model is Missing | Minor |

---

## Level 2 — System

| # | Artifact | Required | Status | Notes |
|---|---|---|---|---|
| 2.1 | System Requirements Specification (SRS) | Yes | ☐ Present ☐ Partial ☐ Missing | Functional + non-functional requirements (security, performance) |
| 2.2 | System Architecture Document (SAD) | Yes | ☐ Present ☐ Partial ☐ Missing | Block diagrams, DFDs, technology stack |
| 2.3 | Interface Control Document (ICD) | Yes | ☐ Present ☐ Partial ☐ Missing | Contracts between subsystems (protocols, data formats) |
| 2.4 | System & Integration Test Plan | Yes | ☐ Present ☐ Partial ☐ Missing | Validates subsystem assembly and system-level behavior |

### Level 2 Gap Severity Rules

| Condition | Severity |
|---|---|
| SRS is Missing | Critical |
| SAD is Missing | Critical |
| ICD is Missing when system has ≥ 2 subsystems | Major |
| ICD is Missing when system is monolithic | Minor |
| Integration Test Plan is Missing | Major |

---

## Level 3 — Component (Library / Package / Service)

| # | Artifact | Required | Status | Notes |
|---|---|---|---|---|
| 3.1 | Component Spec (HLD) | Yes | ☐ Present ☐ Partial ☐ Missing | Structural layout of library, package, or service |
| 3.2 | UML Class Diagrams | Recommended | ☐ Present ☐ Partial ☐ Missing | Class schemas, inheritances, associations |
| 3.3 | UML Sequence Diagrams | Recommended | ☐ Present ☐ Partial ☐ Missing | Temporal execution paths, message passing |
| 3.4 | API / Contract Specifications | Yes (if public API exists) | ☐ Present ☐ Partial ☐ Missing | OpenAPI/Swagger, gRPC .proto, or equivalent |
| 3.5 | Component Test Plan | Yes | ☐ Present ☐ Partial ☐ Missing | Component isolation testing strategy |

### Level 3 Gap Severity Rules

| Condition | Severity |
|---|---|
| Component Spec (HLD) is Missing | Critical |
| API Spec is Missing when public API exists | Critical |
| Component Test Plan is Missing | Major |
| UML Class Diagrams are Missing | Minor |
| UML Sequence Diagrams are Missing | Minor |

---

## Level 4 — Module (Class / Group of Related Functions)

| # | Artifact | Required | Status | Notes |
|---|---|---|---|---|
| 4.1 | Module-Level Design (MLD) | Yes | ☐ Present ☐ Partial ☐ Missing | Behaviors, methods, state management |
| 4.2 | UML Class Diagrams (within component) | Recommended | ☐ Present ☐ Partial ☐ Missing | Class schemas, internal interfaces |
| 4.3 | Module Test Plan | Yes | ☐ Present ☐ Partial ☐ Missing | Module-internal integration tests |

### Level 4 Gap Severity Rules

| Condition | Severity |
|---|---|
| Module-Level Design (MLD) is Missing | Critical |
| Module Test Plan is Missing | Major |
| UML Class Diagrams (within component) are Missing | Minor |

---

## Level 5 — Unit (Function / Method)

| # | Artifact | Required | Status | Notes |
|---|---|---|---|---|
| 5.1 | Unit Spec (LLD) / Micro-specs | Yes (for complex algorithms) | ☐ Present ☐ Partial ☐ Missing | Pseudo-code or detailed logic flows |
| 5.2 | Inline Code Documentation (Javadoc / JSDoc / Doxygen) | Yes | ☐ Present ☐ Partial ☐ Missing | Code-level metadata |
| 5.3 | Unit Test Suite | Yes | ☐ Present ☐ Partial ☐ Missing | Automated tests asserting correct output |
| 5.4 | Static Analysis / Linting Configuration | Recommended | ☐ Present ☐ Partial ☐ Missing | Security vulnerability and style checks |

### Level 5 Gap Severity Rules

| Condition | Severity |
|---|---|
| Unit Test Suite is Missing | Critical |
| Inline Code Documentation is Missing | Major |
| Unit Spec (LLD) / Micro-specs is Missing for complex algorithms (crypto, math, state machines) | Major |
| Unit Spec (LLD) / Micro-specs is Missing for simple CRUD operations | Minor |
| Static Analysis / Linting Configuration is Missing | Minor |

---

## Cross-Level Traceability Checklist

| # | Check | Status | Notes |
|---|---|---|---|
| T.1 | Every Level 2 SRS requirement traces to at least one Level 1 BRD requirement | ☐ Pass ☐ Fail | |
| T.2 | Every Level 3 Component Spec traces to at least one Level 2 SRS requirement | ☐ Pass ☐ Fail | |
| T.3 | Every Level 4 MLD traces to at least one Level 3 Component Spec | ☐ Pass ☐ Fail | |
| T.4 | Every Level 5 Unit Spec traces to at least one Level 4 MLD | ☐ Pass ☐ Fail | |
| T.5 | Every Level 1 UAT scenario has a corresponding Level 2 system/integration test | ☐ Pass ☐ Fail | |
| T.6 | Every Level 2 system test decomposes into Level 3 component tests | ☐ Pass ☐ Fail | |
| T.7 | Every Level 3 component test decomposes into Level 4 module tests | ☐ Pass ☐ Fail | |
| T.8 | Every Level 4 module test decomposes into Level 5 unit tests | ☐ Pass ☐ Fail | |
| T.9 | An RTM exists linking all 5 levels | ☐ Pass ☐ Fail | |

### Traceability Gap Severity Rules

| Condition | Severity |
|---|---|
| RTM does not exist | Critical |
| Any Level 2 requirement has no Level 1 parent | Major |
| Any Level 3 Component Spec has no Level 2 parent | Major |
| Any Level 4 MLD has no Level 3 parent | Major |
| Any Level 5 Unit Spec has no Level 4 parent | Minor (acceptable for utility/helper functions) |
| Verification chain (UAT → System/Integration → Component → Module → Unit) is broken at any point | Major |
