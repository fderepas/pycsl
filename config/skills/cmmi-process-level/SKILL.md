---
name: cmmi-process-level
description: >
  Classifies existing project documentation into the five-level specification
  hierarchy (Business, System, Component, Module, Unit), audits artifact
  coverage at each level, identifies gaps, and produces a severity-ranked gap
  report with remediation recommendations. Use when the user asks to classify
  documentation, check doc coverage, identify missing specs, audit
  documentation completeness, find gaps in their spec hierarchy, assess
  traceability, or review their V-model documentation. Delegates artifact
  generation to the cmmi-documents skill.
document_id: SKILL-CMMI-PLVL-001
version: "1.0"
status: Approved
effective_date: "2026-05-22"
baseline_id: BL-PLVL-001
cmmi_version: "2.0"
practice_areas:
  - "OPD SP 1.1 — Establish Standard Processes"
  - "PQA SP 1.1 — Objectively Evaluate Processes"
  - "RDM SP 1.1 — Develop Requirements"
---

# CMMI Process-Level Documentation Classification and Gap Analysis

## 1. Document Control & Metadata

| Field | Value |
|---|---|
| Document ID | SKILL-CMMI-PLVL-001 |
| Version | 1.0 |
| Status | Approved |
| Effective Date | 2026-05-22 |
| Classification | Configuration Item (CI) — baseline BL-PLVL-001 |

### Revision History

| Version | Date | Description of Change | Author |
|---|---|---|---|
| 1.0 | 2026-05-22 | Initial release; created with CMMI-self-compliant structure | — |

### Approvals

| Name | Role | Date |
|---|---|---|
| *(Process Owner / SEPG)* | Accountable | — |
| *(QA Lead)* | Consulted | — |
| *(Project Manager)* | Informed | — |

---

## 2. Introduction & Context

### 2.1 Purpose

*Practice area: OPD SP 1.1 — establishes a standard process for documentation classification and gap analysis.*

This document defines the process by which an agent classifies existing project
documentation into a five-level specification hierarchy and identifies coverage
gaps. The five levels follow the Top-Down Specification and Bottom-Up Verification
approach (V-Model):

| Level | Name | Focus |
|---|---|---|
| 1 | Business | Business goals, user workflows, domain models |
| 2 | System | Architecture, subsystem decomposition, interfaces |
| 3 | Component | Library/package/service structure, API contracts, design patterns |
| 4 | Module | Class/module structure, internal interfaces, state management |
| 5 | Unit | Function/method logic, algorithms, error handling |

**CMMI v2.0 practice areas addressed:**

- **Organizational Process Definition (OPD SP 1.1):** Defines a reusable classification and audit process.
- **Process Quality Assurance (PQA SP 1.1):** Provides verification criteria for documentation completeness.
- **Requirements Development and Management (RDM SP 1.1):** Supports traceability across specification levels.

### 2.2 Scope

| Applicable | Not applicable |
|---|---|
| Classification of existing documentation into the 5-level hierarchy | Generation of new CMMI-compliant documents (delegate to `cmmi-documents` skill) |
| Gap analysis across all 5 levels | Level 4 (Quantitatively Managed) or Level 5 (Optimizing) CMMI maturity practices |
| Production of a Requirements Traceability Matrix (RTM) | Non-documentation artifacts (source code, binaries, infrastructure) |
| Remediation recommendations with severity ranking | |

### 2.3 Audience

- AI agents executing documentation audit tasks.
- Process engineers assessing project documentation maturity.
- QA auditors validating documentation coverage for CMMI appraisals.
- Project managers reviewing documentation completeness before milestones.

### 2.4 References & Definitions

| Term | Definition |
|---|---|
| V-Model | Systems engineering model where specification flows top-down and verification flows bottom-up |
| RTM | Requirements Traceability Matrix — links requirements across specification levels to verification evidence |
| BRD | Business Requirements Document |
| SRS | System Requirements Specification |
| SAD | System Architecture Document |
| ICD | Interface Control Document |
| HLD | Component Spec (HLD) |
| MLD | Module-Level Design Document |
| LLD | Unit Spec (LLD) |
| UAT | User Acceptance Testing |
| OPD | Organizational Process Definition (CMMI v2.0) |
| PQA | Process Quality Assurance (CMMI v2.0) |
| RDM | Requirements Development and Management (CMMI v2.0) |
| CI | Configuration Item — any artifact baselined under Configuration Management |

### References

| Reference | Location |
|---|---|
| Level definitions — Classification decision tree for the 5 levels. | `references/level-definitions.md` |
| Artifact checklist — Per-level artifact checklists with severity rules. | `references/artifact-checklist.md` |

### Referenced Skills

| Skill | Role in this Skill |
|---|---|
| `cmmi-documents` | Generate new CMMI-compliant artifacts for gaps identified by this skill |

---

## 3. Roles and Responsibilities (RACI Matrix)

*Practice area: PQA SP 1.1 — ensures each audit activity has clear accountability.*

| Activity | Executing Agent¹ | EPG Member | SQA Auditor | Project Manager |
|---|---|---|---|---|
| Collect documentation inventory | R | A | I | C |
| Classify documents by level | R, A | C | I | I |
| Audit artifact coverage per level | R, A | C | C | I |
| Identify and rank gaps by severity | R, A | C | C | I |
| Audit cross-level traceability | R | A | C | I |
| Produce gap report | R, A | I | C | I |
| Recommend remediation actions | R | A | C | C |
| Build Requirements Traceability Matrix | R, A | C | I | I |
| Mark gap report and RTM as CIs | R | A | I | I |
| Approve gap report and RTM | I | R | R | A |
| Trigger cmmi-documents skill for gap filling | R | A | I | I |

¹ *Executing Agent* is the persona that invokes this skill. See `cmmi-agent-roles` for the persona catalog.

---

## 4. Process Architecture (Extended ETVX Model)

*Practice areas: OPD SP 1.1 — defines the classification and audit workflow; RDM SP 1.1 — governs traceability; CM SP 1.1 — governs artifact storage.*

### E — Entry Criteria

All conditions must evaluate to true before the agent begins:

- [ ] A documentation inventory is provided (list of existing documents with titles and locations; an empty inventory is valid for greenfield projects).
- [ ] Project scope is defined (what systems/products the documentation covers).
- [ ] At least one document exists for classification, or the invocation is explicitly marked `greenfield`.

### I — Inputs & Sources

| Input | Source | Format |
|---|---|---|
| Project name | User / project charter | Text (used to resolve output path: `projects/<project>/docs/`) |
| Documentation inventory | User / project repository | List of document titles, paths, or URLs |
| Project scope description | User / project charter | Text |
| Target CMMI Maturity Level (optional) | User | "Level 2" or "Level 3" |
| Level definitions | `references/level-definitions.md` | Markdown decision tree |
| Artifact checklists | `references/artifact-checklist.md` | Markdown checklists with severity rules |

### T — Tasks / Activities

The agent executes the following steps in strict order:

1. **Inventory documents.** List every document provided, recording title, format, location, and date of last update. If the invocation is marked `greenfield`, record an explicit empty inventory and continue.
2. **Classify each document.** Walk the decision tree in `references/level-definitions.md` top-down. Assign each document to exactly one level (1–5). If a document spans multiple levels, assign it to the highest level it addresses and flag cross-level content.
3. **Audit artifact coverage.** For each level, check all artifacts in `references/artifact-checklist.md`. Mark each artifact as Present, Partial, or Missing.
4. **Identify gaps.** For each Missing or Partial artifact, apply the severity rules from `references/artifact-checklist.md` to assign a severity: Critical, Major, or Minor. Critical gaps are escalated via `cmmi-glue` Workflow 3 (SQA Audit & Non-Compliance Escalation).
5. **Audit cross-level traceability.** Execute the traceability checklist in `references/artifact-checklist.md` (items T.1–T.9). Mark each check as Pass or Fail.
6. **Produce gap report.** Generate a structured report containing:
    - Classification matrix (document → level assignment).
    - Per-level coverage summary (Present / Partial / Missing counts).
    - Gap list ranked by severity (Critical → Major → Minor).
    - Traceability audit results.
7. **Recommend remediation.** For each gap, produce a `cmmi-documents` hand-off record that:
    - States what artifact is missing or incomplete.
    - Specifies the target document type and which specification level it belongs to.
    - Defines the document scope & boundaries.
    - Names at least one role for each RACI category (R, A, C, I) to seed the document's RACI matrix.
    - Provides raw process steps from existing material, or states `N/A for new documents`.
    - Declares the target CMMI maturity level.
    - Assigns a priority based on severity.
8. **Build Requirements Traceability Matrix (RTM).** Produce a matrix linking every classified document to its parent requirement (level above) and its verification evidence (level below).
9. **Mark outputs as Configuration Items.** State that the gap report and RTM are CIs to be baselined under CM control.

#### Writing Constraints

| Rule | Requirement |
|---|---|
| No Conversational Prose | Use imperative, professional technical writing. Banned terms: "periodic," "as needed," "appropriate," "generally," "when ready." Use precise conditions and absolute statements. |
| Bidirectional Traceability | Every classified document traces upward to a parent requirement and downward to verification evidence. |
| Keep it Lean | Use tables for the classification matrix, gap report, and RTM. Use bullet points for remediation recommendations. |
| Practice-Area Citation | Cite OPD SP 1.1, PQA SP 1.1, or RDM SP 1.1 in each major section of the output. |

### V — Verification & Validation

*Practice area: PQA SP 1.1 — objective evaluation of process adherence.*

Before delivering the output, the agent must verify all of the following:

- [ ] A complete Revision History block exists in the gap report, starting at v1.0 (or v0.1 for drafts).
- [ ] Every audit activity in this workflow maps to at least one Responsible and one Accountable role in the RACI matrix.
- [ ] The RACI matrix covers every task defined in the Extended ETVX workflow (no task lacks an accountable owner).
- [ ] Entry Criteria were verified as true before classification began.
- [ ] Every document in the inventory is assigned to exactly one specification level.
- [ ] The artifact checklist was executed for all 5 levels, not just levels with existing documents.
- [ ] Gap severities follow the rules in `references/artifact-checklist.md` (no ad-hoc severity assignment).
- [ ] The cross-level traceability checklist (T.1–T.9) was executed and results are included in the gap report (unless tailored per §6).
- [ ] Every remediation recommendation includes document type, scope, at least one seed role, raw process steps (or `N/A for new documents`), target maturity level, and priority.
- [ ] A clear path is defined for metric collection and analysis.
- [ ] All relevant CMMI v2.0 practice areas are cited by ID in the gap report sections.
- [ ] The gap report and RTM are explicitly marked as Configuration Items (CIs) with baseline identifiers.
- [ ] When target maturity level is ≥ 3, tailoring guidelines are noted in the gap report.

### X — Exit Criteria

- [ ] All V — Verification & Validation checks pass.
- [ ] Every document in the inventory is classified.
- [ ] The gap report contains at least: classification matrix, coverage summary, gap list, traceability audit, and remediation recommendations.
- [ ] The RTM links all 5 specification levels (unless tailored per §6).
- [ ] The Accountable role has reviewed the output.

### O — Outputs & Destinations

| Output | Format | Destination |
|---|---|---|
| Classification matrix | Markdown table | Gap report, §1 |
| Per-level coverage summary | Markdown table | Gap report, §2 |
| Severity-ranked gap list | Markdown table | Gap report, §3 |
| Traceability audit results | Markdown table | Gap report, §4 |
| Remediation recommendations | Markdown bullet list with document type, scope, seed role, raw steps, maturity level, and priority | Gap report, §5 |
| Requirements Traceability Matrix (RTM) | Markdown table | `projects/<project>/docs/reports/`, standalone CI |
| Completed V&V checklist | Markdown checklist | Appended to gap report |

---

## 5. Measurement and Metrics

*Practice area: MPM SP 1.1 (Managing Performance and Measurement) — quantitative tracking of documentation maturity.*

| KPI | Formula | Collection Point | Organisational Objective |
|---|---|---|---|
| Coverage rate | (Required artifacts marked Present across all 5 levels) / (total Required artifacts) × 100 | Artifact checklist output | Achieve ≥ 90% documentation coverage across all specification levels (OPD) |
| Gap density | Count of gaps per specification level | Gap report | Reduce documentation gaps to support CMMI appraisal readiness (PQA) |
| Critical gap count | Count of Critical-severity gaps | Gap report | Eliminate all Critical-severity gaps before milestone reviews (RDM) |
| Traceability completeness | (T.1–T.9 checks passing) / 9 × 100 | Traceability audit | Maintain end-to-end traceability across the V-Model for appraisal evidence (RDM) |
| Remediation closure rate | (gaps resolved in follow-up audits) / (gaps identified) × 100 | Comparison of successive gap reports | Close ≥ 80% of identified gaps within one quarter (MPM) |

**Storage:** Record metrics in the project's metrics database or governance dashboard.

### Metric Collection Path

All process-level metrics are collected in gap reports:
`projects/<project>/docs/reports/gap-<topic>-<NNN>.md`

Coverage rate, gap density, and critical gap count are embedded in each gap
report. Successive gap reports enable remediation closure rate tracking. The
EPG Lead reviews trends after each audit. Findings feed into `cmmi-glue`
Workflow 4 (Continuous Improvement).

**Review cadence:** The Process Owner reviews aggregated metrics at each governance cycle (minimum: once per quarter).

---

## 6. Tailoring Guidelines (Mandatory for Level 3+)

*Practice area: OPD SP 1.1 — organizational standard processes must include tailoring criteria.
All deviations follow `cmmi-glue` Workflow 1 (Tailoring Process).*

### Allowed Deviations

| Condition | Permitted Tailoring |
|---|---|
| Project has fewer than 10 documents | RTM may be simplified to a 2-column format (Document → Parent Requirement) without verification linkage. |
| Only 1 or 2 specification levels are in scope | Artifact checklist may be limited to the in-scope levels; out-of-scope levels are noted as "Not Applicable." |
| Target maturity level is Level 2 | Tailoring Guidelines section may be omitted from the gap report. |
| Rapid assessment / triage context | Cross-level traceability audit (T.1–T.9) may be deferred to a follow-up audit; note deferral in the gap report. |
| **Profile-P (PyCSL)** | Classification is pre-declared in `projects/pycsl/PROJECT.md` `spec_kind:` block; gap analysis becomes a delta against the declared mirror rather than a blank-slate classification. T-steps skip levels where the `spec_kind` declares coverage (L1: `csl-from-scratch` skill; L2: `docs/pycsl-*-reference.md` for SY3, `__init__.py` docstring fallback for others; L3: `pycsl-software-architecture` skill; L4: auto via `bin/cmmi-mod-index.py`; L5: in-source `#@` contracts). Gap report groups by system (9 fixed Systems); any system with ≥5 L3-ceiling `# cite:_note:` markers gets a "missing-feature seed" row pointing the Reconciliator at `agent-feature-supervisor.py --propose-feature`. | Developer (single-developer CCB) |

### Approval Authority

All tailoring deviations require written authorization from the **SEPG** or **QA Director** before the agent applies them. Record the deviation and its rationale in the gap report's Revision History.

---

*This document is a Configuration Item (CI) under baseline BL-PLVL-001.
Changes require Change Control Board approval per cmmi-glue Workflow 2.*
