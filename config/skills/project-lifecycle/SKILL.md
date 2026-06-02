---
name: project-lifecycle
description: >-
  Defines the recursive level-based project execution lifecycle: from gap
  analysis through final audit, with each of five specification levels
  (Business, System, Component, Module, Unit) performing a complete
  Synchronize → Delegate → Sub-actors Work → Run Tests → Reconcile cycle.
  Orchestrates all other CMMI skills into a coherent execution sequence,
  mapping each level to the skill it invokes and the role that executes it.
  At every level a Specifier-Verifier-Reconciliator triplet operates; the
  Specifier produces both per-sub-actor specs and a coordination spec. At
  the Unit level, delegation goes to Phase 10 actors (Coder + Validator)
  rather than to further decomposition. Use this skill whenever bootstrapping
  a new project under projects/, planning a project's execution levels,
  determining which role should run which level, deciding what to do next in
  a project, or auditing whether a project followed the prescribed lifecycle.
document_id: SKILL-CMMI-LIFE-001
version: "2.2"
status: Approved
effective_date: "2026-05-22"
baseline_id: BL-LIFE-001
cmmi_version: "2.0"
practice_areas:
  - "OPD SP 1.1 — Establish Standard Processes"
  - "IPM SP 1.1 — Establish the Project's Defined Process"
  - "PP SP 1.1 — Establish Estimates"
  - "PMC SP 1.1 — Monitor the Project Against the Plan"
  - "PQA SP 1.1 — Objectively Evaluate Processes"
---

# Recursive Level-Based Project Lifecycle

## 1. Document Control & Metadata

| Field | Value |
|---|---|
| Document ID | SKILL-CMMI-LIFE-001 |
| Version | 2.2 |
| Status | Approved |
| Effective Date | 2026-05-22 |
| Baseline ID | BL-LIFE-001 |
| CMMI Version | 2.0 |

### Revision History

| Version | Date | Author | Change Summary |
|---|---|---|---|
| 0.1 | 2026-05-22 | Agent (EPG) | Initial draft — codified from bootstrap-cmmi-project-02.txt |
| 1.0 | 2026-05-22 | Agent (EPG) | First approved release: full §1–§6, recursive level-based execution |
| 2.0 | 2026-06-01 | Agent (EPG) | Expand 4→5 levels (Component, Module, Unit); add coordination spec; add cross-cutting obligations; add Phase 10 |
| 2.1 | 2026-06-02 | Agent (EPG) | Add T7.1 feature-plan submission via `agent-feature-supervisor`; new `references/feature-plan-submission.md` |
| 2.2 | 2026-06-02 | Agent (EPG) | Add `references/competency-matrix.md` (skill-to-role); supervisor auto-injects per-phase skills from `**Level:**` tags and logs §5.1 |

### Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| Accountable — EPG Lead | _(pending)_ | | |
| Responsible — Project Manager | _(pending)_ | | |

---

## 2. Introduction & Context

### Purpose

This skill defines the standard project execution lifecycle for all
projects under `projects/`. It implements a **recursive five-level
execution model** where each specification level (Business, System,
Component, Module, Unit) performs a complete cycle driven by a
**Specifier-Verifier-Reconciliator** triplet:

1. **Synchronize.** The Specifier and Verifier work together: the Specifier
   produces per-sub-actor specs and a **coordination spec** (interfaces,
   protocols, shared invariants); the Verifier produces the test plan.
   Neither document is finalized in isolation.
2. **Delegate.** Hand both specs and test plan to sub-actors at the level
   below (or to Phase 10 at the Unit level).
3. **Sub-actors do their work.** Each sub-actor runs its own triplet cycle.
4. **Run the test plan.** The Verifier executes the test plan against the
   assembled work.
5. **Reconcile (only if a test fails).** The Reconciliator diagnoses the
   fault and routes it to the Specifier, the Verifier, or the failing
   sub-actor. The Reconciliator routes; it does not repair.

At the Unit level there is no further decomposition — delegation goes to
**Phase 10 actors** (Coder + Validator) under contracts written by the
Unit-level Specifier.

The lifecycle is the **orchestrator** — it does not generate documents or
run audits itself. Instead, it tells the agent which skill to invoke,
which role to assume, and what the entry/exit criteria are at each level.

This document satisfies CMMI v2.0 practice areas:
- **OPD SP 1.1** — establishes a standard lifecycle process for all projects.
- **IPM SP 1.1** — each project adapts this lifecycle via tailoring.
- **PP SP 1.1** — the phase structure provides a basis for estimation.
- **PMC SP 1.1** — phase entry/exit criteria enable progress monitoring.

### Scope

| In Scope | Out of Scope |
|---|---|
| Five-level recursive lifecycle definition (Business → System → Component → Module → Unit) | Document generation (→ `cmmi-documents`) |
| Level delegation and fan-out (systems → components → modules → units → Phase 10) | Gap analysis methodology (→ `cmmi-process-level`) |
| Level-to-skill mapping | Role definitions (→ `cmmi-agent-roles`) |
| Level-to-role mapping (Specifier, Verifier, Reconciliator) | Governance workflows (→ `cmmi-glue`) |
| Per-sub-actor specs and coordination specs | Directory layout (→ `agent-project-structure`) |
| Entry/exit criteria per level | Inter-agent messaging (→ `communication`) |
| Reconciliation and re-work loop rules | |
| Cross-cutting traceability and cross-level reconciliation routing | |
| Phase 10 delegation (Coder + Validator) at Unit level | |
| Project completion success criteria | |

### Audience

- Project Managers planning project execution.
- EPG members defining or tailoring the lifecycle for a project.
- Business Analysts initiating Phase 1 (gap analysis).
- Any agent determining "what level am I executing?" or "what do I do next?"

### References & Definitions

| Term | Definition |
|---|---|
| Level Execution Task | A complete cycle at one specification level: Synchronize → Delegate → Sub-actors Work → Run Tests → Reconcile |
| Specifier | Defines what a level must produce: per-sub-actor specs and the coordination spec |
| Verifier | Defines the test plan that proves the spec is met, and executes it |
| Reconciliator | On test failure, diagnoses cause and routes fault to Specifier, Verifier, or sub-actor; does not repair |
| Coordination Spec | How sub-actors interact: interfaces, protocols, message orderings, shared invariants |
| Delegation | Handing work to actors at the level below; each delegation can fan out to multiple sub-actors |
| Phase 10 | Leaf delegation at Unit level: Coder implements, Validator verifies, under the Unit Specifier's contract |
| Re-work Loop | A cycle triggered by Reconciliation: the responsible party corrects their output and the level re-executes |
| System | A bounded collection of interacting elements achieving a specific role within the project. Identified at Business Level |
| Component | A modular, replaceable building block of a System (library, crate, package, service). Identified at System Level |
| Module | A class or group of related classes/functions within a Component. Identified at Component Level |
| Unit | A single function or method — the leaf of the level hierarchy. Identified at Module Level |
| BL | Business Level — the hierarchy root directory at `projects/<project>/BL/` |
| SY | System-level directory prefix (e.g. `SY1-PaymentGateway/`) |
| CO | Component-level directory prefix (e.g. `CO1-TransactionEngine/`) |
| MO | Module-level directory prefix (e.g. `MO1-OrderValidator/`) |
| UN | Unit-level directory prefix (e.g. `UN1-ValidateCard/`) |

### References

| Reference | Location |
|---|---|
| Level-based execution (detailed) | `references/v-model-phases.md` |
| Level-to-unit-of-work mapping | `references/level-definitions.md` |
| Directory hierarchy and naming | `references/directory-hierarchy.md` |
| Tailoring profiles | `references/tailoring-profiles.md` |
| Submitting a feature plan to the verification gate | `references/feature-plan-submission.md` |
| Competency matrix (which skills each level/role needs) | `references/competency-matrix.md` |
| Artifact checklist per level | `config/skills/cmmi-process-level/references/artifact-checklist.md` |
| Governance workflows | `config/skills/cmmi-glue/references/workflow-catalog.md` |
| Project structure convention | `config/skills/agent-project-structure/SKILL.md` |
| Design paradigms reference | `config/skills/system-design-paradigms/SKILL.md` |

### Referenced Skills

| Skill | Used In |
|---|---|
| `cmmi-process-level` | Phase 1 (gap analysis), Phase 12 (final re-run) |
| `cmmi-documents` | All level execution tasks (document generation — produces specifications; requirements/ and tests/ are authored directly by Specifier and Verifier roles) |
| `cmmi-agent-roles` | All levels (role assignment, Reconciliation role) |
| `cmmi-glue` | Phase 2 (governance setup), Phase 12 (governance workflows) |
| `cmmi-metrics-collection` | Phase 12 (final metrics collection and baseline update) |
| `agent-project-structure` | Phase 10 leaf task (directory setup). Non-CMMI skill — no ETVX contract; invoked as a structural template, not a formal process |
| `communication` | All levels (inter-agent coordination, re-work routing) |
| `system-design-paradigms` | All level execution tasks (Specify sub-step: specifiers consult design paradigms during architecture and decomposition decisions) |
| `plantuml` | T3–T5 (UML diagrams clarify decomposition boundaries) |
| `spin-modeling` | T3–T4 (formal verification of coordination specs for concurrency correctness) |
| `polish-skill` | Phase 12 (quality audit). Non-CMMI skill — no ETVX contract; invoked as a checklist source for formatting/structure checks |
| `import-existing-code` | T1 retro-engineering path (importing existing codebases into the lifecycle) |

---

## 3. RACI Matrix

*Practice area: OPD SP 1.1 — role-to-level mapping for the project lifecycle.*

| Level / Phase | Activity | Business Analyst / Product Owner² | EPG Lead | System Architect | Project Manager | EPG Member | Configuration Manager | UAT Test Engineer | Reconciliator | Technical Lead | System Test Engineer | Integration Test Engineer | Software Engineer | Module Test Engineer | Unit Test Engineer | SQA Auditor | Metrics Analyst | All stakeholders¹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Phase 1 | Gap Analysis | R | A | C | I | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Phase 2 | Process Documents | — | A | — | I | R | C | — | — | — | — | — | — | — | — | — | — | — |
| Business | Specify (BRD, system decomposition, coordination spec) | R, A | I | C | — | I | C | — | — | — | — | — | — | — | — | C | I | — |
| Business | Define test plan (UAT) | A | — | — | — | — | — | R | — | — | — | — | — | — | — | C | — | — |
| Business | Reconcile failures | A | I | — | — | — | — | C | R | — | — | — | — | — | — | I | — | — |
| System | Specify (SRS/SAD/ICD, component decomposition, coordination spec) | — | I | R, A | — | I | C | — | — | C | — | — | — | — | — | C | I | — |
| System | Define test plan (system + integration tests) | — | — | A | — | — | — | — | — | — | R | C | — | — | — | C | — | — |
| System | Reconcile failures | — | — | A, C | — | — | — | — | R | — | C | — | — | — | — | I | — | — |
| Component | Specify (HLD, module decomposition, coordination spec) | — | — | — | — | — | C | — | — | R, A | — | — | C | — | — | C | I | — |
| Component | Define test plan (component integration tests) | — | — | — | — | — | — | — | — | A | — | R | — | — | C | C | — | — |
| Component | Reconcile failures | — | — | — | — | — | — | — | R | A, C | — | C | — | — | — | I | — | — |
| Module | Specify (MLD, unit decomposition, coordination spec) | — | — | — | — | — | C | — | — | A | — | — | R | — | — | C | I | — |
| Module | Define test plan (module tests) | — | — | — | — | — | — | — | — | A | — | — | C | R | — | C | — | — |
| Module | Reconcile failures | — | — | — | — | — | — | — | R | A | — | — | C | C | — | I | — | — |
| Unit | Specify (LLD, formal annotations, pre/post-conditions) | — | — | — | — | — | C | — | — | A | — | — | R | — | — | C | I | — |
| Unit | Define test plan (unit tests / proofs) | — | — | — | — | — | — | — | — | A | — | — | C | — | R | C | — | — |
| Unit | Reconcile failures | — | — | — | — | — | — | — | R | A | — | — | C | — | C | I | — | — |
| Phase 10 | Implement code (Coder + Validator) | — | — | — | — | — | I | — | — | A | — | — | R | — | — | — | — | — |
| Phase 12 | Final Audit | — | A | — | — | — | — | — | — | — | — | — | — | — | — | R | C | I |

¹ Broadcast notification pattern — not a single persona.
² Combined persona: `config/agents/business-analyst.md` (role: Business Analyst / Product Owner).

**Orchestration tasks (§4.T mapping):**

| Task | Activity | EPG Member | EPG Lead | Configuration Manager | Project Manager | Business Analyst | UAT Test Engineer | Reconciliator | System Architect | System Test Engineer | Technical Lead | Integration Test Engineer | Software Engineer | Module Test Engineer | Unit Test Engineer | SQA Auditor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | Project Initialisation | R | A | C | I | — | — | — | — | — | — | — | — | — | — | — |
| T2 | Execute Business Level | — | A | — | — | R | R | R | — | — | — | — | — | — | — | — |
| T3 | Execute System Level | — | — | — | — | — | — | R | R, A | R | — | — | — | — | — | — |
| T4 | Execute Component Level | — | — | — | — | — | — | R | — | — | R, A | R | — | — | — | — |
| T5 | Execute Module Level | — | — | — | — | — | — | R | — | — | A | — | R | R | — | — |
| T6 | Execute Unit Level | — | — | — | — | — | — | R | — | — | A | — | R | — | R | — |
| T7 | Phase 10 — Code + Validate (leaf) | — | — | I | — | — | — | — | — | — | A | — | R | — | — | — |
| T8 | Level Transition and Delegation Rules | R | A | — | — | — | — | — | — | — | — | — | — | — | — | C |

---

## 4. Process Architecture (Extended ETVX Model)

*Practice areas: OPD SP 1.1 — defines the standard project lifecycle;
IPM SP 1.1 — each project tailors and follows this lifecycle.*

### E — Entry Criteria

All conditions must evaluate to true before starting the lifecycle:

- [ ] A project directory exists at `projects/<project>/` with a `PROJECT.md` charter.
- [ ] The skill library at `config/skills/` contains all referenced skills.
- [ ] Agent personas exist in `config/agents/` for all roles in the RACI matrix.
- [ ] The project charter declares: scope, target CMMI maturity level, and in-scope specification levels.
- [ ] Tailoring profile (S, M, or L) declared in `PROJECT.md` per `references/tailoring-profiles.md`

### I — Inputs & Sources

| Input | Source | Format |
|---|---|---|
| Project name | User / project charter | Text (resolves to `projects/<project>/`) |
| Project charter | `projects/<project>/PROJECT.md` | Markdown |
| Skill library | `config/skills/` | SKILL.md files |
| Agent personas | `config/agents/` | Markdown with YAML frontmatter |
| Source code (if retro-engineering) | `src/` or project-specific path | Source files |

### T — Tasks / Activities

The lifecycle executes Phase 1 (Gap Analysis) and Phase 2 (Process
Documents), then enters **recursive five-level execution** (Tasks T2–T6)
where each specification level performs the five-step Synchronize →
Delegate → Sub-actors Work → Run Tests → Reconcile cycle. Phase 10
(T7) is the leaf action at the Unit level. Phase 12 (Final Audit)
concludes the project. The level scope depends on the project's tailoring
profile (S, M, or L) — see `references/tailoring-profiles.md`.

Level-based execution details are in `references/v-model-phases.md`.

#### T1 — Project Initialisation

1. Verify the project directory structure matches `agent-project-structure`.
2. Verify `PROJECT.md` exists and declares scope, maturity target, and team.
3. Determine if the project is greenfield or retro-engineering; select the tailoring profile (S, M, or L) per `references/tailoring-profiles.md`.
4. Create `projects/<project>/BL/` hierarchy per `references/directory-hierarchy.md`, truncated to the selected profile depth.
5. Create `projects/<project>/message-queues/` (satisfies `communication` entry criteria).
6. Build a documentation inventory for `cmmi-process-level` (empty + `greenfield` flag for new projects).
7. Execute Phase 1 via `cmmi-process-level` (passing inventory + project scope).
8. Execute Phase 2 via `cmmi-documents` (passing document type, scope from `PROJECT.md`, RACI seed from `cmmi-agent-roles`, raw steps or `N/A`).
9. Execute `cmmi-glue` to produce the Workflow Integration Plan (mapping governance workflows to project roles and levels per `cmmi-glue` Workflow 1–4).
10. Record the starting state.

#### T2 — Execute Business Level

**Actors:** Business Analyst (Specifier), UAT Test Engineer (Verifier),
Reconciliator.

Business Analyst defines BRD, use cases, and domain model in
`BL/specifications/main.md`; decomposes business scope into systems;
writes coordination spec (system interfaces, data flows, shared
invariants). For each system, creates `BL/SY<N>-<Name>/` directory
with `requirements/`, `specifications/`, and `tests/` subdirectories,
and populates `requirements/main.md` with per-system requirements
derived from the BL specification. UAT Test Engineer defines UAT test
plan in `BL/tests/main.md`. Each system is delegated to T3.
Five-step cycle: Synchronize → Delegate → Sub-actors Work → Run
Tests → Reconcile. See `references/directory-hierarchy.md` for naming
conventions.

See `references/task-details.md` §T2 for the full activity description.

#### T3 — Execute System Level

**⟳ Iterate once per system identified at Business Level.**

**Actors:** System Architect (Specifier), System Test Engineer (Verifier),
Reconciliator.

System Architect defines SRS/SAD/ICD in `SY<N>-<Name>/specifications/main.md`;
decomposes system into components; writes coordination spec (component
interfaces, protocols, message orderings). For each component, creates
`CO<N>-<Name>/` directory with `requirements/`, `specifications/`,
`tests/`, and `src/` subdirectories, and populates
`requirements/main.md` with per-component requirements derived from
the system specification. System Test Engineer defines system test plan
in `SY<N>-<Name>/tests/main.md`. UML diagrams (`plantuml`) clarify
component boundaries; `spin-modeling` may verify the coordination
spec. Each component is delegated to T4.

See `references/task-details.md` §T3 for the full activity description.

#### T4 — Execute Component Level

**⟳ Iterate once per component identified at System Level.**

**Actors:** Technical Lead (Specifier), Integration Test Engineer (Verifier),
Reconciliator.

Technical Lead defines HLD, class diagrams, API contracts in
`CO<N>-<Name>/specifications/main.md`; decomposes component into
modules; writes coordination spec (calling conventions, shared state,
internal interfaces). For each module, creates `MO<N>-<Name>/`
directory with `requirements/`, `specifications/`, `tests/`, and
`src/` subdirectories, and populates `requirements/main.md` with
per-module requirements. Integration Test Engineer defines component
integration test plan in `CO<N>-<Name>/tests/main.md`. UML diagrams
(`plantuml`) clarify module boundaries; `spin-modeling` may verify
concurrency correctness. Each module is delegated to T5.

See `references/task-details.md` §T4 for the full activity description.

#### T5 — Execute Module Level

**⟳ Iterate once per module identified at Component Level.**

**Actors:** Software Engineer (Specifier), Module Test Engineer (Verifier),
Reconciliator.

Software Engineer defines MLD (behaviors, methods, state management) in
`MO<N>-<Name>/specifications/main.md`; decomposes module into units;
writes coordination spec (call graph, shared invariants). For each
complex unit, creates `UN<N>-<Name>/` directory with `requirements/`,
`specifications/`, `tests/`, and `src/` subdirectories, and populates
`requirements/main.md` with per-unit requirements. Module Test Engineer
defines module test plan in `MO<N>-<Name>/tests/main.md`. UML class
and sequence diagrams (`plantuml`) clarify unit interactions. Each unit
is delegated to T6.

See `references/task-details.md` §T5 for the full activity description.

#### T6 — Execute Unit Level

**⟳ Iterate once per complex unit (function/method with >10 lines, branching
logic, non-obvious algorithm, or error handling) identified at Module Level.**

**Actors:** Software Engineer (Specifier), Unit Test Engineer (Verifier),
Reconciliator.

Software Engineer defines LLD (algorithm pseudo-code, pre/post-conditions,
invariants) in `UN<N>-<Name>/specifications/main.md`. Formal specs
(ACSL, Pearlite) may be used. Unit Test Engineer defines unit test plan
in `UN<N>-<Name>/tests/main.md` (unit tests or proofs). Delegation goes
to Phase 10 (T7): Coder implements in `UN<N>-<Name>/src/`; Validator
verifies.

See `references/task-details.md` §T6 for the full activity description.

#### T7 — Phase 10: Code + Validate (Leaf) ⟳ per unit

Software Engineer implements code in `src/` at the deepest in-scope level;
Validator confirms the implementation satisfies the contract.

**Entry:** T7 is entered from T6 (Profile L) or directly from T3/T4 (Profile
S/M) per the project's tailoring profile. When Profiles S or M skip
intermediate levels, the delegation path from the active lowest level satisfies
T7 entry without requiring T6 completion.

See `references/task-details.md` §T7 for the full activity description.

#### T7.1 — Submitting a feature plan to the verification gate

A planned feature or change is submitted for autonomous classification and
acceptance checking through the **`agent-feature-supervisor`**:

```
./bin/agent-feature-supervisor --feature-file my-great-feature.md
```

The plan document must carry its phases under a `## Implementation surface`
section as `### Phase N — Title` headers, each with a machine-checkable
`**Acceptance:**` block (command + predicate) that is the phase's definition of
done. The supervisor is **gate-only**: it parses, runs the read-only acceptance
claims, and halts `human-needed` rather than editing load-bearing files
(`Module2`–`Module6`, `module6_whyml/*`, `csl.lark`, `formal-semantics/`, the
normative `docs/pycsl-*-reference.md`). This is the lifecycle's bridge from an
approved plan to verified delivery: acceptance claims are re-run on every
invocation, closing the loop ER catches that the gate alone does not (a plan can
pass the gate while shipping nothing).

See `references/feature-plan-submission.md` for the full document shape, bullet
grammar, safety rules, deny-list behavior, and exit codes.

#### T8 — Level Transition and Delegation Rules

| Rule | Requirement |
|---|---|
| Recursive delegation | Each level delegates to the level below; the lowest level (T6 — Unit) delegates to Phase 10 (T7) |
| Fan-out | Delegation can produce multiple sub-actors: several systems from business, several components from a system, several modules from a component, several units from a module |
| Coordination spec | The Specifier at each level must produce both per-sub-actor specs and a coordination spec (interfaces, protocols, shared invariants) |
| Independence constraint | The Specifier, Verifier, and Reconciliator at each level must be different agents/personas |
| Reconciliation loop limit | If the same level fails reconciliation 3 consecutive times without resolution, escalate to SQA / EPG via `cmmi-glue` Workflow 3 (SQA Audit & Non-Compliance Escalation) |
| Cross-level reconciliation | A sub-actor fault at level N triggers reconciliation at level N−1; if N−1 concludes "Specifier fault", it escalates back to level N |
| Tailoring | Levels may be skipped only per the project's tailoring profile or with EPG approval documented in PROJECT.md |
| Phase 2 parallel allowance | Phase 2 (Process Docs) may run in parallel with the start of T2 (Business Level) |
| Level completion | A level is complete when its test plan passes and all delegated sub-level work is accepted |

#### Writing Constraints

| Rule | Requirement |
|---|---|
| No Conversational Prose | Level descriptions use imperative verbs and binary conditions. |
| Level Completeness | Every level execution must produce specification artifacts (per-sub-actor specs + coordination spec) and test plan artifacts. |
| Traceability | Every spec at level N must trace upward to level N+1 requirements and downward to level N−1 sub-actors. |
| Coordination Spec Required | The Specifier must explicitly define how sub-actors interact, separate from what each sub-actor does individually. |
| Directory Hierarchy Compliance | All artifacts must be stored in the prescribed directory hierarchy (`BL/SY<N>-<Name>/CO<N>-<Name>/...`) per `references/directory-hierarchy.md`. No artifacts outside the hierarchy. |

### V — Verification & Validation

*Practice area: PQA SP 1.1 — objective evaluation of lifecycle adherence.*

Before marking a project lifecycle as complete, verify:

- [ ] Phase 1 (Gap Analysis) and Phase 2 (Process Documents) have been executed.
- [ ] All in-scope specification levels have completed their execution cycle (Synchronize → Delegate → Sub-actors Work → Run Tests → Reconcile).
- [ ] Delegation fan-out was executed for all sub-units at each level (all systems, components, modules, units).
- [ ] Level entry/exit criteria were checked and recorded at each transition.
- [ ] The independence constraint was respected (Specifier ≠ Verifier ≠ Reconciliator at each level) (unless tailored per §6).
- [ ] Coordination specs exist at every level and were validated against test failures.
- [ ] All reconciliation loops terminated (either tests pass or escalation was triggered).
- [ ] Cross-level reconciliation routing was correctly applied (sub-actor faults escalated downward; Specifier faults escalated upward when warranted).
- [ ] The directory hierarchy follows the prescribed naming convention (`BL/SY<N>-<Name>/CO<N>-<Name>/MO<N>-<Name>/UN<N>-<Name>/`) per `references/directory-hierarchy.md`.
- [ ] Every level directory contains `requirements/`, `specifications/`, and `tests/` subdirectories with populated `main.md` files.
- [ ] `src/` directories exist at CO, MO, and UN levels (or at the deepest in-scope level per tailoring profile).
- [ ] A Requirements Traceability Matrix (RTM) links all in-scope levels.
- [ ] The final gap re-run (Phase 12) shows 0 Critical and 0 Major gaps (unless tailored per §6).
- [ ] All test suites pass at all in-scope levels.
- [ ] The SQA audit report is filed with 0 open NCRs (non-conformances are escalated via `cmmi-glue` Workflow 3).
- [ ] Reconciliation logs exist for each level where re-work occurred.

### X — Exit Criteria

- [ ] All V — Verification & Validation checks pass.
- [ ] The project's success criteria (from PROJECT.md) are met.
- [ ] The EPG Lead has approved the lifecycle completion.

### O — Outputs & Destinations

| Output | Format | Destination |
|---|---|---|
| Gap analysis report | Markdown | `projects/<project>/docs/reports/` |
| Process documents (QA plan, CM procedure) | Markdown | `projects/<project>/docs/process/` |
| Requirements (per-level) | Markdown | `projects/<project>/BL/.../requirements/main.md` |
| Specifications (per-level) | Markdown | `projects/<project>/BL/.../specifications/main.md` |
| Test plans and test results (per-level) | Markdown | `projects/<project>/BL/.../tests/main.md` |
| Source code | Source code | `projects/<project>/BL/.../src/` (CO, MO, UN levels) |
| Reconciliation logs | Markdown | `projects/<project>/docs/reports/` |
| RTM | Markdown | `projects/<project>/docs/reports/` |
| SQA audit report | Markdown | `projects/<project>/docs/audits/` |
| Metrics report | Markdown | `projects/<project>/docs/reports/` |

---

## 5. Measurement and Metrics

*Practice area: MPM SP 1.1 — quantitative tracking of lifecycle execution.*

| KPI | Formula | Collection Point | Organisational Objective |
|---|---|---|---|
| Level completion rate | (levels completed) / (levels in scope) × 100 | Level exit-criteria records | 100% level execution for all projects |
| Specification-verification pairing rate | (levels with passing tests) / (levels with specifications) × 100 | Level records | 100% pairing — no level left unverified |
| Gap closure rate | (gaps closed) / (gaps identified in Phase 1) × 100 | Phase 12 re-run vs Phase 1 | 100% Critical + Major gaps closed |
| Test pass rate per level | (tests passing) / (total tests) × 100 per level | Test execution reports | >95% pass rate at each level |
| Traceability completeness | (requirements with ≥1 test) / (total requirements) × 100 | RTM | 100% traceability |
| Independence compliance | (levels with 3 distinct actors) / (total levels) × 100 | Level records | 100% independence |
| Reconciliation re-work count | Total re-work loops triggered per level per project | Reconciliation logs | Minimize re-work; trend downward over projects |
| Fault attribution distribution | Percentage of faults classified as Specifier / Verifier / Level-below | Reconciliation logs | Identify systemic weaknesses by fault type |

### Metric Collection Path

All lifecycle metrics are collected in `projects/<project>/docs/reports/metrics-collection-<NNN>.md`. Each level completion appends a row. The EPG Lead reviews at Phase 12; the Metrics Analyst archives the final version alongside the SQA audit report. Findings feed into `cmmi-glue` Workflow 4 (Continuous Improvement Loop) to refine the lifecycle for future projects.

---

## 6. Tailoring Guidelines

*Practice area: OPD SP 1.1 — controlled adaptation of the lifecycle.*

| Deviation | Conditions for Approval | Approval Authority |
|---|---|---|
| Skip Phase 2 (Process Docs) | Process documents already exist from a prior project | EPG Lead |
| Skip Module Level execution (T5) | Component has ≤3 units with no complex coordination | Technical Lead |
| Skip Unit Level execution (T6) for simple functions | Functions are ≤10 lines with no branching logic | Technical Lead |
| Merge System + Component Level execution (T3 + T4) | System has only 1 component (single-package system) | System Architect |
| Skip Phase 12 formal audit | Project is a prototype / proof-of-concept with no production deployment | EPG Lead |
| Reduce fan-out iterations | Sub-actor count is <3; batch into a single level iteration | Technical Lead |
| Omit Reconciliator role | Single-level project with no sub-level delegation | EPG Lead |

### Pre-Approved Tailoring Profiles

Three pre-approved profiles right-size the lifecycle without requiring the
full cmmi-glue Workflow 1 ceremony. See `references/tailoring-profiles.md`
for selection criteria, level scope, and document scope.

| Profile | Levels | Execution Scope | Governance |
|---|---|---|---|
| S (Small) | L1 + L2 | T2 + T3 + T7 + Phase 12 | PM self-approves |
| M (Medium) | L1–L3 | T2 + T3 + T4 + T7 + Phase 12 | EPG fast-track |
| L (Large) | L1–L5 | T2 + T3 + T4 + T5 + T6 + T7 + Phase 12 | Full Workflow 1 ceremony |
| **P (PyCSL)** | L1–L5 by system per `PROJECT.md` | T2 + T3 + per-system T4–T6 + T7=no-op + Phase 12 | Single-developer CCB; commit SHA = CR-ID. See `cmmi-tailoring-plan.md`. |

Profile selection is recorded in `PROJECT.md` and is a Configuration Item.
Any profile change after project start requires Change Control (`cmmi-glue` Workflow 2).

### Profile-P specific bindings

Under Profile-P (PyCSL): the Business-level operational playbook is
[`config/skills/csl-from-scratch/SKILL.md`](../csl-from-scratch/SKILL.md).
Its §0.5 Squeeze Strategy is the BL requirements set; T2 (Execute
Business Level) is satisfied by maintaining csl-from-scratch as the
canonical BL plan and by running the per-Squeeze coverage check
(`bin/cmmi-audit.sh` C8 step 5). T7 (Phase 10 Coder step) is a no-op
under Profile-P: code already exists in `src/<package>/`; the
Validator step is `pycsl --proof` + `bin/run-reference-tests.sh`.
Source dirs at CO/MO/UN are never materialised under `BL/`; they live
at `<src_root>` from `PROJECT.md`. L4 Module specs are auto-generated
indices via `bin/cmmi-mod-index.py`; L5 Unit specs are the in-source
`#@` contracts (no separate files).

All tailoring deviations must be recorded in the project's `PROJECT.md` under a "Tailoring Deviations" section, with reference to this skill (SKILL-CMMI-LIFE-001) and the approving authority's sign-off.

---
*This document is a Configuration Item (CI) under baseline BL-LIFE-001. Changes require Change Control Board approval per `cmmi-glue` Workflow 2.*
