---
name: import-existing-code
description: >-
  Defines the process for importing an existing codebase into the CMMI
  framework by retro-specifying it bottom-up through the V-model (Unit →
  Module → Component → System → Business), then designing test plans
  top-down, and finally implementing and running all tests. Use this skill
  whenever importing, onboarding, or retro-documenting an existing codebase
  under the CMMI lifecycle framework.
document_id: SKILL-IMPORT-001
version: "2.0"
status: Approved
effective_date: "2026-05-29"
baseline_id: BL-IMPORT-001
cmmi_version: "2.0"
practice_areas:
  - "OPD SP 1.1 — Establish Standard Processes"
  - "RDM SP 1.1 — Maintain Bidirectional Traceability"
  - "PQA SP 1.1 — Objectively Evaluate Processes"
  - "CM SP 1.1 — Identify Configuration Items"
  - "MPM SP 1.1 — Manage Process Performance"
---

# Import Existing Code into CMMI Framework

## 1. Document Control & Metadata

| Field | Value |
|---|---|
| Document ID | SKILL-IMPORT-001 |
| Version | 2.0 |
| Status | Approved |
| Effective Date | 2026-05-29 |
| Classification | Configuration Item (CI) — baseline BL-IMPORT-001 |

### Revision History

| Version | Date | Description of Change | Author |
|---|---|---|---|
| 1.0 | 2026-05-22 | Initial release; process derived from skill2rag pilot import | — |
| 2.0 | 2026-05-29 | Restructured to CMMI-compliant §1–§6 + ETVX format; lessons learned moved to references/ | — |

### Approvals

| Name | Role | Date |
|---|---|---|
| *(Process Owner)* | Accountable | — |
| *(QA Lead)* | Consulted | — |

---

## 2. Introduction & Context

### Purpose

*Practice area: OPD SP 1.1 — defines a standard process for importing
existing codebases into the CMMI lifecycle.*

When a codebase already exists but was not built under the CMMI lifecycle,
this skill defines how to **retro-fit** it: scaffold a proper CMMI project,
produce specifications at every V-model level, design test plans, implement
tests, and generate the formal documents that make the codebase CMMI-compliant.

The skill was derived from the first pilot import (`src/skill2rag/`) and
explicitly addresses every gap discovered during that pilot. See
`references/lessons-learned.md` for the full gap analysis.

### Scope

| In Scope | Out of Scope |
|---|---|
| Project scaffolding (`projects/<name>/`) | Greenfield project creation (→ `project-lifecycle`) |
| Retro-specification of existing code (L5→L1) | Modifying production code to pass tests |
| Test plan design (L1→L5) | Deployment and release management |
| Test implementation and execution | Ongoing maintenance processes |
| Formal document generation (BRD, SRS, SAD, HLD, MLD, LLD) | Training new developers |
| PlantUML diagrams at each level | |
| Traceability matrix creation | |
| SQA summary report | |
| Project-level compliance audit | |

### Audience

- Software Engineers importing existing codebases.
- EPG Members overseeing the import process.
- SQA Auditors validating compliance of imported projects.

### References & Definitions

| Term | Definition |
|---|---|
| Retro-specification | Creating specifications from existing code by reading the implementation and documenting its intent, contracts, and architecture |
| Import | The full process of bringing an existing codebase under CMMI process governance |
| BRD | Business Requirements Document (Level 1) |
| SRS/SAD | System Requirements Specification / System Architecture Document (Level 2) |
| HLD | High-Level Design — Component specification (Level 3) |
| MLD | Module-Level Design — Module specification (Level 4) |
| LLD | Low-Level Design — Unit specification (Level 5) |

### References

| Reference | Location |
|---|---|
| Import checklist | `references/import-checklist.md` |
| Lessons learned (skill2rag pilot) | `references/lessons-learned.md` |

### Referenced Skills

| Skill | Used In |
|---|---|
| `project-lifecycle` | Provides the V-model framework this skill operates within |
| `cmmi-documents` | Document generation at each level (BRD, SRS, HLD, MLD, LLD) |
| `plantuml` | UML diagrams at each level |
| `cmmi-metrics-collection` | KPI recording during Phase 3 |
| `communication` | Inter-agent message tracking |
| `cmmi-coherency-audit` | Framework-level validation (config/skills/ scope, not project-level) |
| `cmmi-glue` | Tailoring (Workflow 1), change control (Workflow 2), non-conformance escalation (Workflow 3), continuous improvement (Workflow 4) |

---

## 3. RACI Matrix

*Practice area: PQA SP 1.1 — ensures each import activity has clear accountability.*

| Phase / Activity | Software Engineer | Technical Lead | EPG Member | SQA Auditor | Configuration Manager | Metrics Analyst |
|---|---|---|---|---|---|---|
| Phase 0 — Project Scaffolding | R | A | C | I | I | I |
| Phase 1 — Retro-Specify (Go Up V) | R | A | I | I | I | I |
| Phase 2 — Design Test Plans (Go Down V) | R | A | I | C | I | I |
| Phase 3 — Execute Tests & Reports | R | A | I | C | R | C |
| Phase 4 — Compliance Audit | I | I | R | A | C | I |
| Lessons learned capture | R | A | C | I | I | I |

---

## 4. Process Architecture (Extended ETVX Model)

*Practice areas: OPD SP 1.1 — defines the import workflow; RDM SP 1.1 —
governs traceability; CM SP 1.1 — governs artifact storage.*

### E — Entry Criteria

All conditions must evaluate to true before starting the import:

- [ ] The codebase exists and compiles/runs (or at least can be read).
- [ ] Source code is located at `src/<name>/` (or a declared alternative path).
- [ ] The `project-lifecycle` skill has been loaded.
- [ ] The target CMMI maturity level has been established for the project (required by `cmmi-documents` and `cmmi-glue` entry criteria).
- [ ] Python/language tooling is available for test execution.
- [ ] A project directory exists at `projects/<name>/` (or will be created in Phase 0).

### I — Inputs & Sources

| Input | Source | Format |
|---|---|---|
| Existing source code | `src/<name>/` | Source files |
| Project name | User input | Text (resolves to `projects/<name>/`) |
| Skill library | `config/skills/` | SKILL.md files |
| Agent personas | `config/agents/` | Markdown with YAML frontmatter |

### T — Tasks / Activities

The import executes in five phases. Detailed lessons learned from the
skill2rag pilot are in `references/lessons-learned.md`.

> **Path convention:** This skill uses `<name>` as the project path placeholder
> (e.g., `projects/<name>/`). This is equivalent to `<project>` used in other
> skills — both resolve to the project directory name.

#### Phase 0 — Project Scaffolding

Create the CMMI project structure per `config/skills/project-lifecycle/references/directory-hierarchy.md`:

```text
projects/<name>/
├── PROJECT.md                   ← project charter (scope, source location, team)
├── BL/                          ← V-model execution tree
│   ├── requirements/main.md
│   ├── specifications/main.md   ← Business (BRD, use cases)
│   ├── tests/main.md            ← UAT test plan
│   └── SY<N>-<Name>/            ← one dir per system
│       ├── requirements/main.md
│       ├── specifications/main.md
│       ├── tests/main.md
│       └── CO<N>-<Name>/        ← one dir per component
│           ├── requirements/main.md
│           ├── specifications/main.md
│           ├── tests/main.md
│           ├── src/
│           └── ...              ← MO/UN levels per profile
├── docs/
│   ├── reports/                 ← SQA summary, metrics, traceability matrix
│   ├── diagrams/                ← PlantUML outputs (.puml + rendered)
│   └── audits/                  ← project-level compliance audits
├── message-queues/              ← communication tracking
└── inputs/                      ← original source references
```

The `PROJECT.md` must include: Document ID (`PROJ-<NAME>-001`), source code
location, test suite location, and import method (`import-existing-code`).

Invocation: `/plan run import-existing-code for <name>` — sources at
`src/<name>/`, tests at `tests/<name>/`, artifacts at `projects/<name>/`.

#### Phase 1 — Go Up the V (Retro-Specify)

Work bottom-up, reading existing code to produce specifications.

| Step | Level | Input | Output | Skills Invoked |
|---|---|---|---|---|
| 1.1 | L5 Unit | Source functions | Unit contracts (pre/post, algorithm, errors) | `cmmi-documents` (LLD) |
| 1.2 | L4 Module | Source files | Module specs (API, coordination, use cases) | `cmmi-documents` (MLD) |
| 1.3 | L3 Component | Packages/dirs | Component specs (contract, interface, data flow) | `cmmi-documents` (HLD), `plantuml` |
| 1.4 | L2 System | Full codebase | System spec (architecture, NFRs, config) | `cmmi-documents` (SRS/SAD), `plantuml` |
| 1.5 | L1 Business | System context | Business spec (goals, use cases, acceptance) | `cmmi-documents` (BRD), `plantuml` |

**Mandatory at each level:**

- [ ] PlantUML diagram — at least one UML diagram per level
- [ ] RACI matrix — who is R/A/C/I for each artifact
- [ ] Traceability entry — spec traces upward and downward
- [ ] Document ID — formal ID per `cmmi-documents` convention

#### Phase 2 — Go Down the V (Design Test Plans)

Work top-down, designing test plans at each level.

| Step | Level | Input | Output | Test ID Prefix |
|---|---|---|---|---|
| 2.1 | L1 Business | Business spec | Acceptance test plan | AT-NNN |
| 2.2 | L2 System | System spec | System test plan | ST-NNN |
| 2.3 | L3 Component | Component specs | Component test plans | CT-NNN |
| 2.4 | L4 Module | Module specs | Module test plans | MT-NNN |
| 2.5 | L5 Unit | Unit specs | Unit test plans | UT-NNN |

**Mandatory at each level:**

- [ ] Every test case traces to a spec requirement
- [ ] Test IDs use formal prefixes (AT/ST/CT/MT/UT + sequential number)

#### Phase 3 — Execute Tests and Produce Reports

| Step | Level | Action | Exit Criterion |
|---|---|---|---|
| 3.1 | L5 Unit | Implement + run unit tests | All UT-NNN pass |
| 3.2 | L4 Module | Implement + run module tests | All MT-NNN pass |
| 3.3 | L3 Component | Implement + run component tests | All CT-NNN pass |
| 3.4 | L2 System | Implement + run system tests | All ST-NNN pass |
| 3.5 | L1 Business | Implement + run acceptance tests | All AT-NNN pass |
| 3.6 | — | Generate SQA summary report | Report committed |

**Mandatory at Phase 3 completion:**

- [ ] SQA Summary Report at `projects/<name>/docs/reports/sqa-import-summary.md`
- [ ] Metrics collection per `cmmi-metrics-collection`
- [ ] Communication log entries tracked per `communication` skill

**Testing strategy:** Mock only external I/O (API endpoints, CLI subprocesses,
filesystem side-effects). Use deterministic fake data (e.g., fixed-dimension
vectors for embeddings) so assertions are stable and reproducible. This pattern
was validated in the skill2rag pilot — see `references/lessons-learned.md`.

#### Phase 4 — Project Compliance Audit

Validates that the imported project meets CMMI standards. Distinct from
`cmmi-coherency-audit` which covers `config/skills/` only.

| Check | What It Verifies |
|---|---|
| P4.1 | `projects/<name>/PROJECT.md` exists with all required fields |
| P4.2 | Spec documents exist at all in-scope levels under `BL/` hierarchy per `config/skills/project-lifecycle/references/directory-hierarchy.md` |
| P4.3 | Every spec has a document ID and traces to the level above/below |
| P4.4 | PlantUML diagrams exist for L1 (use case), L2 (sequence), L3 (component), L4 (class) |
| P4.5 | Test files exist at all 5 levels under `tests/<name>/` |
| P4.6 | All tests pass (`pytest tests/<name>/ --import-mode=importlib`) |
| P4.7 | SQA summary report exists at `docs/reports/sqa-import-summary.md` |
| P4.8 | Traceability matrix exists at `docs/reports/traceability-matrix.md` |
| P4.9 | RACI matrices present in L1–L3 specs |
| P4.10 | Communication log entries exist under `message-queues/` |

**Exit criterion:** All P4.1–P4.10 pass, or each gap is documented with a
remediation plan in `projects/<name>/docs/audits/`.

#### Writing Constraints

| Rule | Requirement |
|---|---|
| No Conversational Prose | Use imperative, professional technical writing. Banned terms: "periodic," "as needed," "appropriate," "generally," "when ready." |
| Bidirectional Traceability | Every spec traces upward to parent requirement and downward to test evidence. |
| Practice-Area Citation | Cite relevant SP IDs (OPD SP 1.1, RDM SP 1.1, PQA SP 1.1, CM SP 1.1) in output documents. |

### V — Verification & Validation

*Practice area: PQA SP 1.1 — objective evaluation of import process adherence.*

Before delivering the final import, verify:

- [ ] Phase 0 created a complete project structure per `config/skills/project-lifecycle/references/directory-hierarchy.md`.
- [ ] Phase 1 produced specifications at all 5 V-model levels (L1–L5).
- [ ] Each specification has a PlantUML diagram, RACI matrix, traceability entry, and document ID.
- [ ] Phase 2 produced test plans at all 5 levels with formal test IDs.
- [ ] Phase 3 executed all tests and produced an SQA summary report.
- [ ] Phase 4 compliance audit passed all P4.1–P4.10 checks (or gaps documented). Non-conformances escalate per `cmmi-glue` Workflow 3 (SQA Audit & Non-Compliance Escalation).
- [ ] Metrics collected per `cmmi-metrics-collection`.
- [ ] Communication log entries exist for inter-level hand-offs.
- [ ] All outputs are marked as Configuration Items with baseline identifiers.

### X — Exit Criteria

- [ ] All V — Verification & Validation checks pass.
- [ ] All test suites pass at all 5 levels.
- [ ] The SQA summary report is committed.
- [ ] The compliance audit (Phase 4) has 0 Critical and 0 Major gaps.

### O — Outputs & Destinations

| Output | Format | Destination |
|---|---|---|
| Project charter | Markdown | `projects/<name>/PROJECT.md` |
| L1 Business spec | Markdown | `projects/<name>/BL/specifications/main.md` |
| L2 System spec | Markdown | `projects/<name>/BL/SY<N>-<Name>/specifications/main.md` |
| L3 Component specs | Markdown | `projects/<name>/BL/.../CO<N>-<Name>/specifications/main.md` |
| L4 Module specs | Markdown | `projects/<name>/BL/.../MO<N>-<Name>/specifications/main.md` |
| L5 Unit specs | Markdown | `projects/<name>/BL/.../UN<N>-<Name>/specifications/main.md` |
| PlantUML diagrams | `.puml` | `projects/<name>/docs/diagrams/` |
| Test suite | Python/language | `tests/<name>/` |
| SQA summary report | Markdown | `projects/<name>/docs/reports/sqa-import-summary.md` |
| Traceability matrix | Markdown | `projects/<name>/docs/reports/traceability-matrix.md` |
| Communication log | JSON | `projects/<name>/message-queues/` |
| Metrics report | Markdown | `projects/<name>/docs/reports/metrics-collection-*.md` (collected by `cmmi-metrics-collection`) |
| Compliance audit | Markdown | `projects/<name>/docs/audits/` |

---

## 5. Measurement and Metrics

*Practice area: MPM SP 1.1 — quantitative tracking of the import process.*

| KPI | Formula | Collection Point | Organisational Objective |
|---|---|---|---|
| Retro-spec coverage | (levels with specs) / 5 × 100 | Phase 1 completion | 100% spec coverage |
| Test plan coverage | (levels with test plans) / 5 × 100 | Phase 2 completion | 100% test plan coverage |
| Test pass rate | (tests passing) / (total tests) × 100 | Phase 3 execution | >95% pass rate |
| Compliance audit pass rate | (P4 checks passing) / 10 × 100 | Phase 4 | 100% compliance |
| Traceability completeness | (requirements with ≥1 test) / (total requirements) × 100 | Phase 4 RTM | 100% traceability |

### Metric Collection Path

All import metrics are collected in `projects/<name>/docs/reports/metrics-collection-<NNN>.md` via the `cmmi-metrics-collection` skill (canonical owner of the metrics report path). The SQA summary report aggregates test metrics. Findings feed into `cmmi-glue` Workflow 4 (Continuous Improvement Loop).

---

## 6. Tailoring Guidelines

*Practice area: OPD SP 1.1 — controlled adaptation of the import process.
All deviations follow `cmmi-glue` Workflow 1 (Tailoring Process).*

| Deviation | Conditions for Approval | Approval Authority |
|---|---|---|
| Merge L4 and L5 into a single spec | Small codebase (<5 files) | Technical Lead |
| Omit L3 component level | Single-component system | Technical Lead |
| Simplify mocking strategy | No external APIs | Software Engineer |
| Split import + greenfield | New code added alongside existing code; use `project-lifecycle` for new code | EPG Lead |
| **Profile-P (PyCSL):** source stays in `src/<package>/`, never under `BL/.../src/`; L4 indices auto-generated by `bin/cmmi-mod-index.py`; L5 = in-source `#@` contracts (no `UN<N>-<Name>/` dirs created); BL L1 spec is an include of `config/skills/csl-from-scratch/SKILL.md`. Phase 0 reads the 9-system table from `PROJECT.md`. Phase 4 audit P4.2 accepts the `<src_root>` pointer instead of requiring `BL/.../src/`. | Project is PyCSL (single-developer CCB) | Developer (self-approve per `should-we-cmmi-or-not.md` §8) |

All tailoring deviations must be recorded in the project's `PROJECT.md`
under a "Tailoring Deviations" section with reference to this skill
(SKILL-IMPORT-001) and the approving authority's sign-off.

---

*This document is a Configuration Item (CI) under baseline BL-IMPORT-001.
Changes require Change Control Board approval per `cmmi-glue` Workflow 2.*
