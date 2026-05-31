# Specification Level Definitions — Classification Decision Tree

This reference defines the five specification levels and provides binary
classification criteria an agent uses to assign an existing document to
exactly one level.

## How to Use This File

For each document under review, walk the decision tree top-down. A document
belongs to the **first level whose criteria it satisfies**. If a document
spans multiple levels, classify it at the highest (most abstract) level it
addresses and note the cross-level content in the gap report.

---

## Level 1 — Business ("The Why and What")

### Classification Criteria

A document belongs to Level 1 when **all** of the following are true:

- [ ] The document describes business goals, commercial justification, or operational objectives.
- [ ] The document defines user-facing workflows, pain points, or value propositions.
- [ ] The document does **not** reference specific technology stacks, protocols, or system components.
- [ ] The document uses domain language (e.g., "Customer," "Transaction," "Subscription") without mapping those terms to software constructs.

### Characteristic Artifacts

| Artifact | Description |
|---|---|
| Business Requirements Document (BRD) | Commercial and operational goals |
| Product Vision | Strategic product direction and market justification |
| User Stories / Epic Specifications | User-centric requirements with acceptance criteria ("As a… I want to… So that…") |
| Use Case Blueprints | Step-by-step actor-system interaction narratives |

### Specification Processes at This Level

- Requirements Elicitation (stakeholder interviews, workshops, market analysis).
- Domain Modeling (business entities and their real-world interactions, technology-independent).

### Expected Verification & Validation

- User Acceptance Testing (UAT): real-life scenarios executed by end-users or product owners.

---

## Level 2 — System ("The Architecture & Components")

### Classification Criteria

A document belongs to Level 2 when **all** of the following are true:

- [ ] The document translates business use cases into technical system capabilities.
- [ ] The document decomposes a product into systems, subsystems, or system-level services.
- [ ] The document defines interfaces, protocols, or data contracts between macro-components.
- [ ] The document does **not** describe internal class structures, methods, or algorithmic logic.

### Characteristic Artifacts

| Artifact | Description |
|---|---|
| System Requirements Specification (SRS) | Functional and non-functional requirements (security, performance, scalability) |
| System Architecture Document (SAD) | Block diagrams, data-flow diagrams (DFDs), technology stack definitions |
| Interface Control Document (ICD) | Contracts between subsystems (protocols, data formats, API boundaries) |

### Specification Processes at This Level

- System Decomposition (mapping business use cases to software systems or subsystems).
- Interface Definition (protocols, data contracts, and component boundaries).

### Expected Verification & Validation

- System Testing: validating that the entire system behaves as expected under load.
- Integration Testing: validating that all subsystems assemble and communicate correctly.

---

## Level 3 — Component ("The Library / Package / Service")

### Classification Criteria

A document belongs to Level 3 when **all** of the following are true:

- [ ] The document describes replaceable building blocks such as libraries, crates, packages, or services.
- [ ] The document defines interfaces, contracts, or dependencies between components.
- [ ] The document specifies design patterns applied at the component boundary or service composition layer.
- [ ] The document does **not** describe internal class structures, module internals, or individual methods within a component.

### Characteristic Artifacts

| Artifact | Description |
|---|---|
| Component Spec (HLD) | Structural layout of a specific library, package, or service |
| UML Class Diagrams | Visual schemas of types and interfaces exposed by the component |
| UML Sequence Diagrams | Temporal execution paths and message passing across component boundaries |
| API / Contract Specifications | Formal schemas (OpenAPI/Swagger, gRPC `.proto`) for public interfaces |

### Specification Processes at This Level

- Component Decomposition: partitioning the system into replaceable libraries, packages, or services.
- Interface & Pattern Definition: defining contracts, dependencies, and design patterns at the component boundary.

### Expected Verification & Validation

- Component Testing: testing an individual library, package, or service in isolation.
- API Automation: verifying public interfaces against contract specifications.
- Service Virtualization / Mocking: simulating neighboring components for isolated testing.

---

## Level 4 — Module ("The Class / Group of Related Functions")

### Classification Criteria

A document belongs to Level 4 when **all** of the following are true:

- [ ] The document describes classes, modules, or groups of related classes/functions inside a component.
- [ ] The document defines internal interfaces, responsibilities, state management, or calling conventions between those modules.
- [ ] The document specifies collaboration patterns among internal classes or modules without descending into individual function logic.
- [ ] The document does **not** describe individual function implementations or algorithmic steps.

### Characteristic Artifacts

| Artifact | Description |
|---|---|
| Module-Level Design (MLD) | Behaviors, methods, state management for a class or group of related functions |
| UML Class Diagrams | Class schemas within a component |
| UML Sequence Diagrams | Intra-component message flows |
| Module Test Plan | Module-internal integration tests |

### Specification Processes at This Level

- Object-Oriented Design: class decomposition, responsibility assignment, and method signatures.
- Module Interface Design: defining internal interfaces, state transitions, and calling conventions.

### Expected Verification & Validation

- Module Testing: testing classes or groups of functions in isolation.
- Intra-Component Integration Testing: verifying collaborations between modules inside a component.

---

## Level 5 — Unit ("The Function / Method")

### Classification Criteria

A document belongs to Level 5 when **all** of the following are true:

- [ ] The document describes individual functions, methods, or algorithms.
- [ ] The document specifies exact logic, loops, state transitions, or mathematical operations.
- [ ] The document defines explicit boundary conditions, pre/post-conditions, and error handling for individual routines.
- [ ] The document operates at the granularity of a single function or method.

### Characteristic Artifacts

| Artifact | Description |
|---|---|
| Unit Spec (LLD) | Pseudo-code or detailed logic flows, pre/post-conditions, invariants |
| Inline Code Documentation | Javadoc, JSDoc, Doxygen, or equivalent code-level metadata |

### Specification Processes at This Level

- Algorithmic Design: exact logic, loops, state transitions, and math for each function.
- Error Handling Strategy: explicit boundary conditions, inputs, outputs, and safe failure modes (exceptions).

### Expected Verification & Validation

- Unit Testing: automated test suites (JUnit, PyTest) asserting correct output for given input.
- Static Code Analysis & Linting: automated checks for security vulnerabilities and style adherence.
- Code Reviews: peer examination of function-level logic and error handling.

---

## Cross-Level Traceability

Documents at adjacent levels must trace to each other. The traceability
direction is:

```
Level 1 (Business)
    ↓ traces down to
Level 2 (System)
    ↓ traces down to
Level 3 (Component)
    ↓ traces down to
Level 4 (Module)
    ↓ traces down to
Level 5 (Unit)
```

**Upward verification:** Each lower level validates the level above it. Unit
tests (Level 5) verify function correctness, which supports module tests
(Level 4), which support component tests (Level 3), which feed system and
integration tests (Level 2), which underpin UAT (Level 1).

A Requirements Traceability Matrix (RTM) must link every artifact at each
level to its parent requirement at the level above and its verification
evidence at the level below.
