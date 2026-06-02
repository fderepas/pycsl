# Level-Based Execution Reference

This reference defines the recursive level-based execution model for the
project lifecycle. Each of five specification levels (Business, System,
Component, Module, Unit) performs a complete Specifier-Verifier-Reconciliator
cycle. Phase 10 (Code + Validate) is the leaf action at the Unit level.

All directory paths follow the naming convention defined in
`references/directory-hierarchy.md`.

---

## Recursive Execution Diagram

```
  Phase 1  Gap Analysis
      ↓
  Phase 2  Process Documents
      ↓
  T2  BUSINESS LEVEL  [BL/]
      [Synchronize → Delegate → Sub-actors → Tests → Reconcile]
      │
      ├── FOR EACH SYSTEM ────────────────────────────────────────────────┐
      │                                                                    │
      │  T3  SYSTEM LEVEL  [BL/SY<N>-<Name>/]                             │
      │      [Synchronize → Delegate → Sub-actors → Tests → Reconcile]    │
      │      │                                                             │
      │      ├─(Profile S)──────────── T7  PHASE 10 (leaf) ───────────   │
      │      │                                                             │
      │      ├── FOR EACH COMPONENT ──────────────────────────────────┐   │
      │      │                                                         │   │
      │      │  T4  COMPONENT LEVEL  [.../CO<N>-<Name>/]               │   │
      │      │      [Synch → Delegate → Sub → Tests → Reconcile]       │   │
      │      │      │                                                  │   │
      │      │      ├─(Profile M)───── T7  PHASE 10 (leaf) ────────   │   │
      │      │      │                                                  │   │
      │      │      ├── FOR EACH MODULE ──────────────────────────┐   │   │
      │      │      │                                              │   │   │
      │      │      │  T5  MODULE LEVEL  [.../MO<N>-<Name>/]       │   │   │
      │      │      │      [Synch → Del → Sub → Tests → Rec]       │   │   │
      │      │      │      │                                       │   │   │
      │      │      │      ├── FOR EACH UNIT ─────────────────┐   │   │   │
      │      │      │      │                                   │   │   │   │
      │      │      │      │  T6  UNIT LEVEL  [.../UN<N>-<Name>/]  │   │   │
      │      │      │      │      [Synch → Del → Phase 10 → Tests → Rec]   │
      │      │      │      │      │                            │   │   │   │
      │      │      │      │      └── T7  PHASE 10 (leaf)      │   │   │   │
      │      │      │      │          [.../UN<N>-<Name>/src/]  │   │   │   │
      │      │      │      │          (Profile L)              │   │   │   │
      │      │      │      │                                   │   │   │   │
      │      │      │      └───────────────────────────────────┘   │   │   │
      │      │      │                                              │   │   │
      │      │      └──────────────────────────────────────────────┘   │   │
      │      │                                                         │   │
      │      └─────────────────────────────────────────────────────────┘   │
      │                                                                    │
      └────────────────────────────────────────────────────────────────────┘
      ↓
  Phase 12  Final Audit
```

## The Five-Step Workflow at Every Level

At each level the same cycle operates, driven by the
Specifier-Verifier-Reconciliator triplet:

```
  ┌───────────────────────────────────────────────────────────┐
  │  1. SYNCHRONIZE  Specifier and Verifier work together.    │
  │                  Specifier produces:                       │
  │                    • Per-sub-actor specs (what each does)  │
  │                    • Coordination spec (how they interact) │
  │                  Verifier produces the test plan.          │
  │                  Neither is finalized in isolation.        │
  │                            ↓                               │
  │  2. DELEGATE     Hand specs + test plan to sub-actors     │
  │                  at the level below (fan-out to N actors)  │
  │                  or to Phase 10 at Unit level.             │
  │                            ↓                               │
  │  3. SUB-ACTORS   Each sub-actor runs its own triplet      │
  │     DO WORK      cycle (or Coder-Validator loop at        │
  │                  Phase 10). When all deliver, assembly     │
  │                  is ready.                                 │
  │                            ↓                               │
  │  4. RUN TESTS    Verifier executes the test plan against  │
  │                  the assembled work.                       │
  │                            ↓                               │
  │  5. RECONCILE    Reconciliator diagnoses failure:          │
  │                  • Specifier fault (spec or coordination   │
  │                    spec wrong)                             │
  │                  • Verifier fault (test plan wrong)        │
  │                  • Sub-actor fault (propagate downward)    │
  │                            ↓                               │
  │     ┌─ PASS ──→ Level complete                            │
  │     └─ FAIL ──→ Reconciliator diagnoses responsible       │
  │                 party; that party re-works, then           │
  │                 loop back to the appropriate step:         │
  │                 • Specifier fault  → step 1               │
  │                 • Verifier fault   → step 4               │
  │                 • Sub-actor fault  → step 3               │
  └───────────────────────────────────────────────────────────┘
```

> **Termination:** If the same level fails reconciliation 3 consecutive
> times without resolution, escalate to SQA / EPG governance.

> **Reference impl (Profile-P, L5).** The annotation `coordinator.py` runs this
> exact routing: a reconcile **Specifier fault** (`fault_class: specifier`) →
> re-decompose the file via `agent-splitter` (L4) instead of re-patching the unit;
> a **Sub-actor fault** → `agent-script-update`. Termination is mechanized: exit 73
> on a 3× recurring recommendation (or an L5↔L4 re-decompose cap), exit 72 on max
> retries — each emits a Workflow-3 **NCR** (`metrics/ncr/`) into the escalation
> chain bound in `cmmi-glue/SKILL.md`.

## The Specifier's Coordination Responsibility

The Specifier at level N writes two distinct kinds of specification:

- **Per-sub-actor specs** — what each sub-actor at level N−1 must do,
  in isolation.
- **Coordination spec** — how the sub-actors interact: the interfaces,
  protocols, message orderings, shared invariants. The coordination spec
  is what makes the assembly correct given that each sub-actor is correct
  on its own.

This split matters at reconciliation time. If a test fails and each
sub-actor demonstrably meets its individual spec, then either the per-
sub-actor specs were too weak (something the assembly needs is missing
from all of them) or the coordination spec was wrong. Either way, the
Specifier is responsible — and is the party Reconciliation routes to.

## Cross-Cutting Obligations

### Traceability

Every spec at level N must trace **upward** to one or more requirements
at level N+1 (so the question "why does this exist?" has an answer) and
**downward** to the sub-actors at level N−1 that realize it (so "where
is this satisfied?" has an answer). Without traceability, the levels
become parallel checklists rather than a linked hierarchy, and
reconciliation has no path to follow when escalation across levels is
needed.

### Reconciliation Routing Across Levels

A sub-actor fault at level N triggers reconciliation at level N−1. But
sometimes the right answer at N−1 is itself "Specifier fault" — meaning
level N−1's spec was wrong, which means level N's coordination spec for
the sub-actors was misaligned with what they could deliver. In that case
the fault escalates back up to level N. The Reconciliator at each level
must be willing to recognize this case and push back upward when
warranted.

---

## Phase 1 — Gap Analysis

| Field | Value |
|---|---|
| Level | Cross-level |
| Skill invoked | `cmmi-process-level` |
| Role | Business Analyst |

### Entry Criteria

- [ ] Project directory exists at `projects/<project>/`.
- [ ] `PROJECT.md` is baselined with scope and maturity target.

### Activities

1. Inventory all existing artifacts (code, docs, skills, personas).
2. Classify each into specification levels 1–5 using `cmmi-process-level`.
3. Audit coverage using `config/skills/cmmi-process-level/references/artifact-checklist.md`.
4. Identify infrastructure gaps (package manifest, tests, linting, config).
5. Produce severity-ranked gap report.

> **Greenfield note:** If T1 identifies a greenfield project, Activity 1 produces an empty project-document inventory. Invoke `cmmi-process-level` with the `greenfield` flag so the empty inventory satisfies the documentation-inventory entry criterion and the run proceeds directly to artifact-checklist gap identification.

### Exit Criteria

- [ ] Gap report exists at `projects/<project>/docs/reports/`.
- [ ] All gaps are classified by severity (Critical, Major, Minor).

### Outputs

| Output | Destination |
|---|---|
| Gap analysis report | `projects/<project>/docs/reports/gap-<app>-001.md` |

---

## Phase 2 — Process Documents

| Field | Value |
|---|---|
| Level | Cross-level (governance) |
| Skill invoked | `cmmi-documents` + `cmmi-glue` |
| Role | EPG Member → Configuration Manager |

### Entry Criteria

- [ ] Phase 1 is complete (gap report identifies which process docs are needed).

> **Note:** The `cmmi-glue` skill invoked in this phase requires project scope,
> target CMMI maturity level, assigned organisational roles, and identified
> specification levels. These prerequisites are guaranteed by the
> `project-lifecycle` overall entry criteria (§4.E) and Phase 1 outputs.

### Activities

1. Generate Quality Assurance Plan (QA-PLAN).
2. Generate Configuration Management Procedure (CM-PROC).
3. Generate Measurement Plan (MPM-PLAN).
4. Generate Workflow Integration Plan.
5. Baseline all generated documents under CM control.

### Exit Criteria

- [ ] All process documents exist in `projects/<project>/docs/process/`.
- [ ] The Workflow Integration Plan exists in `projects/<project>/docs/reports/` and is baselined as a CI.
- [ ] Each process document passes the cmmi-documents 9-point V&V checklist.

### Outputs

| Output | Destination |
|---|---|
| QA Plan | `projects/<project>/docs/process/` |
| CM Procedure | `projects/<project>/docs/process/` |
| Measurement Plan | `projects/<project>/docs/process/` |
| Workflow Integration Plan | `projects/<project>/docs/reports/` |

---

## T2 — Business Level Execution

| Field | Value |
|---|---|
| Level | 1 — Business |
| Unit of work | The whole application |
| Skills invoked | `cmmi-documents` |
| Actors | Business Analyst (Specifier), UAT Test Engineer (Verifier), Reconciliator |

### Entry Criteria

- [ ] Phase 1 is complete.

### Activities

**Step 1 — Synchronize.** The Business Analyst and UAT Test Engineer work
together:

The Business Analyst:
1. Writes or validates the BRD (business requirements, goals, stakeholders).
2. Defines usage requirements: who uses the system, how, and why.
3. Identifies and enumerates **systems** — the distinct bounded collections
   of interacting elements that compose the application.
4. Writes user stories with acceptance criteria.
5. Writes use case blueprints (actor-system interaction narratives).
6. Drafts domain model (business entities, relationships).
7. Writes the **coordination spec**: how the systems interact (interfaces,
   data flows, shared invariants between systems).

The UAT Test Engineer:
1. Formalises each BRD acceptance criterion into an executable UAT scenario.
2. Defines concrete use cases with expected inputs and outputs.
3. Writes the UAT plan: scope, environment, test data, pass/fail criteria.
4. Maps each UAT scenario to its originating BR (traceability).

The two synchronize so that the test plan exercises the specification —
neither document is finalized in isolation.

**Step 2 — Delegate.** Each system identified in Step 1 becomes one
invocation of T3 (System Level Execution). System-level actors receive both
the business specification and the business test plan.

**Step 3 — Sub-actors do their work.** Each System runs its own
Specifier-Verifier-Reconciliator cycle. When all Systems deliver, the
business-level assembly is ready.

**Step 4 — Run tests.** The UAT Test Engineer executes the UAT test plan
against the assembled work.

**Step 5 — Reconcile.** If tests pass, the Business Level is complete. If
tests fail, the Reconciliator diagnoses the fault:
- **Specifier fault:** the coordination among systems is wrong, or the
  decomposition is flawed — even if all systems individually delivered
  correct results. The Business Analyst re-does the specification.
- **Verifier fault:** the UAT test plan contains errors. The UAT Test
  Engineer corrects the test plan.
- **Sub-actor fault:** one or more systems did not deliver results
  conforming to their specifications. The fault propagates downward into
  the failing System's own reconciliation.

### Exit Criteria

- [ ] BRD exists with numbered requirements and acceptance criteria.
- [ ] Systems are enumerated with names, paths, and descriptions.
- [ ] Coordination spec exists for inter-system interactions.
- [ ] UAT plan exists with executable scenarios.
- [ ] Every BRD requirement has at least one UAT scenario.
- [ ] UAT tests pass (or reconciliation loop has concluded).

### Outputs

| Output | Destination |
|---|---|
| BRD | `projects/<project>/BL/specifications/main.md` |
| User stories | `projects/<project>/BL/specifications/` |
| Use case blueprints | `projects/<project>/BL/specifications/` |
| Domain model | `projects/<project>/BL/specifications/` |
| Coordination spec (systems) | `projects/<project>/BL/specifications/` |
| UAT Plan | `projects/<project>/BL/tests/main.md` |
| Per-system requirements | `projects/<project>/BL/SY<N>-<Name>/requirements/main.md` |
| Reconciliation log (if re-work occurred) | `projects/<project>/docs/reports/` |

---

## T3 — System Level Execution

**⟳ Iterate once per system identified at Business Level.**

| Field | Value |
|---|---|
| Level | 2 — System |
| Unit of work | A bounded collection of interacting elements |
| Skills invoked | `cmmi-documents` |
| Actors | System Architect (Specifier), System Test Engineer (Verifier), Reconciliator |

### Entry Criteria

- [ ] T2 Step 1 is complete (systems are enumerated).
- [ ] The current system's scope and boundaries are defined.

### Activities

**Step 1 — Synchronize.** The System Architect and System Test Engineer work
together:

The System Architect:
1. Writes SRS: functional and non-functional requirements.
2. Writes SAD: architecture, block diagrams, data flow, technology stack.
3. Writes ICD: external interfaces, inter-system contracts.
4. Enumerates **components** — the modular, replaceable building blocks
   (libraries, crates, packages, services) that compose this system.
5. Writes the **coordination spec**: component interfaces, protocols,
   message orderings, shared invariants between components.

The System Test Engineer:
1. Writes system test plan: end-to-end scenarios validating SRS requirements.
2. Writes integration test plan: component assembly and inter-component data flow.
3. Defines test data, environment, pass/fail criteria.
4. Maps each test to its originating SRS requirement.

UML use-case and sequence diagrams are appropriate at this level.

**Step 2 — Delegate.** Each component identified in Step 1 becomes one
invocation of T4 (Component Level Execution). Component-level actors receive
both the system specification and the system test plan.

**Step 3 — Sub-actors do their work.** Each Component runs its own
Specifier-Verifier-Reconciliator cycle.

**Step 4 — Run tests.** When all Component Level work is received, execute
the system test plan and integration test plan.

**Step 5 — Reconcile.** If tests pass, the System Level is complete. If tests
fail, the Reconciliator diagnoses the fault:
- **Specifier fault:** the coordination among components is wrong, or the
  decomposition is flawed. The System Architect re-does the specification.
- **Verifier fault:** the system test plan contains errors. The System Test
  Engineer corrects the test plan.
- **Sub-actor fault:** one or more components did not deliver results
  conforming to their specifications. The fault propagates downward into
  the failing Component's own reconciliation.

### Exit Criteria

- [ ] SRS, SAD, and ICD exist for this system.
- [ ] Components are enumerated with paths and responsibilities.
- [ ] Coordination spec exists for inter-component interactions.
- [ ] System and integration test plans exist.
- [ ] Every SRS requirement has at least one test case.
- [ ] System tests pass (or reconciliation loop has concluded).

### Outputs

| Output | Destination |
|---|---|
| SRS | `projects/<project>/BL/SY<N>-<Name>/specifications/main.md` |
| SAD | `projects/<project>/BL/SY<N>-<Name>/specifications/` |
| ICD | `projects/<project>/BL/SY<N>-<Name>/specifications/` |
| Coordination spec (components) | `projects/<project>/BL/SY<N>-<Name>/specifications/` |
| System test plan | `projects/<project>/BL/SY<N>-<Name>/tests/main.md` |
| Integration test plan | `projects/<project>/BL/SY<N>-<Name>/tests/` |
| Per-component requirements | `projects/<project>/BL/SY<N>-<Name>/CO<N>-<Name>/requirements/main.md` |
| Reconciliation log (if re-work occurred) | `projects/<project>/docs/reports/` |

---

## T4 — Component Level Execution

**⟳ Iterate once per component identified at System Level.**

| Field | Value |
|---|---|
| Level | 3 — Component |
| Unit of work | A library / crate / package / service |
| Skills invoked | `cmmi-documents` |
| Actors | Technical Lead (Specifier), Integration Test Engineer (Verifier), Reconciliator |

### Entry Criteria

- [ ] T3 Step 1 is complete for the parent system (components are enumerated).

### Activities

**Step 1 — Synchronize.** The Technical Lead and Integration Test Engineer
work together:

The Technical Lead:
1. Writes HLD: classes, dataclasses, relationships, state management.
2. Defines the component's contract: behavior provided and interface exposed.
3. Defines use cases for callers of the component (API, message protocol).
4. Enumerates **modules** — classes or groups of related classes/functions
   within this component.
5. Writes the **coordination spec**: calling conventions, shared state,
   and internal interfaces between modules.

The Integration Test Engineer:
1. Writes component test plan: integration tests at the component boundary.
2. Defines test cases for normal operation, boundary conditions, and errors.
3. Maps each test to its originating HLD contract element.

**Step 2 — Delegate.** Each module identified in Step 1 becomes one
invocation of T5 (Module Level Execution). Module-level actors receive both
the component specification and the component test plan.

**Step 3 — Sub-actors do their work.** Each Module runs its own
Specifier-Verifier-Reconciliator cycle.

**Step 4 — Run tests.** When all Module Level work is received, execute the
component test plan.

**Step 5 — Reconcile.** If tests pass, the Component Level is complete. If
tests fail, the Reconciliator diagnoses the fault:
- **Specifier fault:** the coordination among modules is wrong, or the
  decomposition is flawed. The Technical Lead re-does the specification.
- **Verifier fault:** the component test plan contains errors. The
  Integration Test Engineer corrects the test plan.
- **Sub-actor fault:** one or more modules did not deliver results
  conforming to their specifications. The fault propagates downward into
  the failing Module's own reconciliation.

### Exit Criteria

- [ ] HLD exists for this component.
- [ ] Component contract and API are documented.
- [ ] Modules are enumerated with responsibilities.
- [ ] Coordination spec exists for inter-module interactions.
- [ ] Component test plan exists.
- [ ] Component tests pass (or reconciliation loop has concluded).

### Outputs

| Output | Destination |
|---|---|
| HLD | `projects/<project>/BL/.../CO<N>-<Name>/specifications/main.md` |
| API contract spec | `projects/<project>/BL/.../CO<N>-<Name>/specifications/` |
| Coordination spec (modules) | `projects/<project>/BL/.../CO<N>-<Name>/specifications/` |
| Component test plan | `projects/<project>/BL/.../CO<N>-<Name>/tests/main.md` |
| Per-module requirements | `projects/<project>/BL/.../CO<N>-<Name>/MO<N>-<Name>/requirements/main.md` |
| Reconciliation log (if re-work occurred) | `projects/<project>/docs/reports/` |

---

## T5 — Module Level Execution

**⟳ Iterate once per module identified at Component Level.**

| Field | Value |
|---|---|
| Level | 4 — Module |
| Unit of work | A class / group of related classes or functions |
| Skills invoked | `cmmi-documents` |
| Actors | Software Engineer (Specifier), Module Test Engineer (Verifier), Reconciliator |

### Entry Criteria

- [ ] T4 Step 1 is complete for the parent component (modules are enumerated).

### Activities

**Step 1 — Synchronize.** The Software Engineer and Module Test Engineer
work together:

The Software Engineer:
1. Writes MLD: module responsibility, behaviors, methods, state management.
2. Defines use cases for callers of the module.
3. Defines public method/function signatures with types.
4. Enumerates **units** — individual functions and methods in this module.
5. Writes the **coordination spec**: call graph, shared invariants between
   units. UML class and sequence diagrams are appropriate here.

The Module Test Engineer:
1. Writes module test plan: module-internal integration tests exercising
   the module's public behavior.
2. Defines test cases for normal operation, boundary conditions, and errors.
3. Maps each test to its originating MLD element.

**Step 2 — Delegate.** Each unit identified in Step 1 becomes one invocation
of T6 (Unit Level Execution). Unit-level actors receive both the module
specification and the module test plan.

**Step 3 — Sub-actors do their work.** Each Unit runs its own
Specifier-Verifier-Reconciliator cycle.

**Step 4 — Run tests.** When all Unit Level work is received, execute the
module test plan.

**Step 5 — Reconcile.** If tests pass, the Module Level is complete. If
tests fail, the Reconciliator diagnoses the fault:
- **Specifier fault:** the coordination among units is wrong, or the
  decomposition is flawed. The Software Engineer re-does the specification.
- **Verifier fault:** the module test plan contains errors. The Module Test
  Engineer corrects the test plan.
- **Sub-actor fault:** one or more units did not deliver results conforming
  to their specifications. The fault propagates downward into the failing
  Unit's own reconciliation.

### Exit Criteria

- [ ] MLD exists for this module.
- [ ] Units are enumerated with signatures and responsibilities.
- [ ] Coordination spec exists for inter-unit interactions.
- [ ] Module test plan exists.
- [ ] Module tests pass (or reconciliation loop has concluded).

### Outputs

| Output | Destination |
|---|---|
| MLD (Module-Level Design) | `projects/<project>/BL/.../MO<N>-<Name>/specifications/main.md` |
| Coordination spec (units) | `projects/<project>/BL/.../MO<N>-<Name>/specifications/` |
| Module test plan | `projects/<project>/BL/.../MO<N>-<Name>/tests/main.md` |
| Per-unit requirements | `projects/<project>/BL/.../MO<N>-<Name>/UN<N>-<Name>/requirements/main.md` |
| Reconciliation log (if re-work occurred) | `projects/<project>/docs/reports/` |

---

## T6 — Unit Level Execution

**⟳ Iterate once per complex unit (function/method) identified at Module Level.**

| Field | Value |
|---|---|
| Level | 5 — Unit |
| Unit of work | A single function or method |
| Skills invoked | `cmmi-documents` |
| Actors | Software Engineer (Specifier), Unit Test Engineer (Verifier), Reconciliator |

### Entry Criteria

- [ ] T5 Step 1 is complete for the parent module (units are enumerated).
- [ ] The unit is classified as "complex" (>10 lines, branching logic,
  non-obvious algorithm, or error handling).

### Activities

**Step 1 — Synchronize.** The Software Engineer and Unit Test Engineer work
together:

The Software Engineer:
1. Writes LLD: algorithm pseudo-code, step-by-step logic, data transformations.
2. Defines inputs and outputs — arguments, return values, side effects.
3. Writes formal annotations: pre-conditions, post-conditions, invariants.
4. Documents boundary conditions and edge cases.
5. Specifies error handling strategy.
6. Optionally writes formal specification (ACSL for Frama-C, Pearlite for
   Rust), making pre/post-conditions machine-checkable.

The Unit Test Engineer:
1. Writes unit tests verifying pre/post-conditions from the LLD.
2. Tests boundary conditions and error paths.
3. Writes property-based tests where applicable.
4. Defines coverage target (>80% line coverage).
5. Maps each test to its originating LLD / formal annotation.
6. If formal specs are used, writes unit proofs with loop invariants.

**Step 2 — Delegate.** Because there is no level below, delegation goes to
**Phase 10** (T7): the Coder implements the function body; the Validator
verifies it. Both receive the contract (from the Specifier) and the
verification expectations (from the Verifier).

**Step 3 — Sub-actors do their work.** The Coder-Validator consensus loop
operates. The Coder implements; the Validator confirms.

**Step 4 — Run tests.** When code is delivered, execute the unit tests
(or run the proof tool: Frama-C, Creusot, etc.).

**Step 5 — Reconcile.** If tests pass, the Unit Level is complete. If tests
fail, the Reconciliator diagnoses the fault:
- **Specifier fault:** the contract is too weak, a precondition is missing,
  or the contract is unrealizable. The Software Engineer re-does the
  specification.
- **Verifier fault:** the unit test or proof obligation is wrong. The Unit
  Test Engineer corrects the test plan.
- **Sub-actor fault:** the code implementation does not satisfy the contract.
  Re-delegate to Phase 10 (T7).

### Exit Criteria

- [ ] LLD exists for this unit (or docstring suffices for simple units).
- [ ] Pre/post-conditions are specified.
- [ ] Unit tests exist for all complex units.
- [ ] Code coverage ≥80%.
- [ ] All tests pass (or reconciliation loop has concluded).

### Outputs

| Output | Destination |
|---|---|
| LLD / micro-spec | `projects/<project>/BL/.../UN<N>-<Name>/specifications/main.md` |
| Unit test suite | `projects/<project>/BL/.../UN<N>-<Name>/tests/main.md` |
| Coverage report | `projects/<project>/docs/reports/` |
| Reconciliation log (if re-work occurred) | `projects/<project>/docs/reports/` |

---

## T7 — Phase 10: Code + Validate (Leaf) ⟳ per unit

| Field | Value |
|---|---|
| Level | 5 — Unit (leaf action) |
| Skill invoked | `agent-project-structure` (directory setup) |
| Actors | Coder (Software Engineer), Validator |

### Entry Criteria

- [ ] A contract exists for the current unit (LLD from T6, or equivalent specification from T3/T4 when Profiles S/M skip intermediate levels).

> **Profile-aware entry:** T7 is entered from T6 (Profile L) or directly from
> T3/T4 (Profiles S/M) per the project's tailoring profile. When Profiles S or
> M skip intermediate levels, the delegation path from the active lowest level
> satisfies T7 entry without requiring T6 completion.

### Activities

1. The Coder implements or updates code to match the LLD / contract from T6.
2. Add missing error handling identified in T6.
3. Complete all docstrings to match formal annotations.
4. Add type hints for all function signatures.
5. Create package manifest (`pyproject.toml` or equivalent) if absent.
6. Create configuration files referenced in code.
7. Update `.gitignore` for derived artifacts.
8. The Validator confirms the implementation satisfies the contract.

### Exit Criteria

- [ ] Code compiles/runs without errors.
- [ ] All functions have docstrings.
- [ ] Package manifest exists with declared dependencies.
- [ ] Validator confirms contract satisfaction.

### Outputs

| Output | Destination |
|---|---|
| Updated source code | `projects/<project>/BL/.../src/` (CO, MO, or UN level) |
| Package manifest | Repository root |
| Configuration files | `config/` |

---

## Phase 12 — Final Audit & Process Verification

| Field | Value |
|---|---|
| Level | Cross-level |
| Skill invoked | `cmmi-glue` (Workflow 3 project SQA closure) + `cmmi-process-level` + `cmmi-metrics-collection` + optional `cmmi-coherency-audit` |
| Role | Project SQA Auditor + Metrics Analyst |

### Entry Criteria

- [ ] All in-scope level execution tasks (T2–T6) are complete with passing tests.

### Activities

1. Project SQA Auditor: execute `cmmi-glue` Workflow 3 over project-instance artifacts under `projects/<project>/` and assemble the project SQA closure package.
2. Project SQA Auditor: audit all in-scope specifications, test evidence, and governance records against the 9-point V&V checklist and summarize the final V&V status.
3. Project SQA Auditor: verify the traceability chain BRD → SRS → HLD → MLD → LLD → Code → Tests and build or update the final Requirements Traceability Matrix (RTM).
4. Project SQA Auditor: verify coordination specs exist at each level, all test suites pass, reconciliation logs are complete, and cross-level reconciliation routing was correctly applied.
5. Project SQA Auditor: issue, track, and close NCRs for non-conformances; confirm the final NCR log shows 0 open NCRs.
6. Metrics Analyst: collect and file lifecycle metrics.
7. Re-run Phase 1 gap analysis to verify all Critical/Major gaps are closed.
8. If the project modified any skills under `config/skills/`, invoke `cmmi-coherency-audit` as a separate framework-level check on those skill-library changes.

### Exit Criteria

- [ ] 0 Critical and 0 Major gaps remaining.
- [ ] 0 open NCRs.
- [ ] RTM links all in-scope levels bidirectionally.
- [ ] All test suites pass.
- [ ] Project SQA closure report, final NCR log, final RTM, and metrics collection report are filed.
- [ ] All reconciliation loops terminated without open escalations.
- [ ] If `config/skills/` was modified, the framework coherency audit is completed and filed.

### Outputs

| Output | Destination |
|---|---|
| Project SQA closure report (V&V summary) | `projects/<project>/docs/audits/` |
| Final NCR log / closure status | `projects/<project>/docs/audits/` |
| Final RTM | `projects/<project>/docs/reports/` |
| Metrics collection report | `projects/<project>/docs/reports/` |
| Final gap re-run | `projects/<project>/docs/reports/` |
| Optional framework coherency audit report (if `config/skills/` changed) | `projects/<project>/docs/audits/` |

---

## Level-to-Skill Quick Reference

| Level / Phase | Skill(s) | Specifier | Verifier | Reconciliator |
|---|---|---|---|---|
| Phase 1 | `cmmi-process-level` | Business Analyst | — | — |
| Phase 2 | `cmmi-documents`, `cmmi-glue` | EPG Member | — | — |
| T2 Business | `cmmi-documents` | Business Analyst | UAT Test Engineer | Reconciliator |
| T3 System | `cmmi-documents` | System Architect | System Test Eng. | Reconciliator |
| T4 Component | `cmmi-documents` | Technical Lead | Integration Test Eng. | Reconciliator |
| T5 Module | `cmmi-documents` | Software Engineer | Module Test Eng. | Reconciliator |
| T6 Unit | `cmmi-documents` | Software Engineer | Unit Test Engineer | Reconciliator |
| T7 Phase 10 | `agent-project-structure` | — (Coder + Validator) | — | — |
| Phase 12 | `cmmi-glue`, `cmmi-process-level`, `cmmi-metrics-collection` (+ optional `cmmi-coherency-audit`) | — | Project SQA Auditor | — |

---

## How the Levels Connect — The V-Model in Practice

Specifications flow **top-down**: Business defines what Systems must do;
each System spec defines what its Components must do; each Component spec
defines what its Modules must do; each Module spec defines what its Units
must do; and Units delegate to Phase 10 for implementation.

Verification flows **bottom-up**: Phase 10 produces verified Units; Units
are assembled into Modules and tested; Modules into Components and tested;
Components into Systems and tested; Systems into the full project and
tested at the Business level.

Reconciliation is the third flow, and it goes **in whichever direction the
fault traces to**: a sub-actor fault flows downward into the sub-actor's
own cycle; a Specifier fault flows back upward when the spec at the level
above turns out to have been the real problem; a Verifier fault stays at
the current level.
