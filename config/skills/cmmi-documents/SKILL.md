---
name: cmmi-documents
description: >
  Transforms unstructured processes, raw project outlines, or legacy
  documentation into highly structured, CMMI v2.0-compliant organizational
  artifacts. Enforces RACI accountability, Extended ETVX process architecture,
  measurement frameworks, and tailoring guidelines to satisfy CMMI appraisal
  criteria up to Maturity Level 3 (Defined). Use when the user asks to write
  a QA plan, create an SRS, draft a process document, make a PMP, write a
  configuration management procedure, turn content into a CMMI document,
  format something for CMMI, create a specification, write a process-level
  plan, create a procedure for a CMMI v2.0 practice area, draft an SOP,
  write a standard operating procedure, create a policy document, build a
  workflow doc, or produce a template for a CMMI artifact.
document_id: SKILL-CMMI-DOC-001
version: "1.0"
status: Approved
effective_date: "2026-05-22"
baseline_id: BL-DOC-001
cmmi_version: "2.0"
practice_areas:
  - "OPD SP 1.1 — Establish Standard Processes"
  - "PQA SP 1.1 — Objectively Evaluate Processes"
---

# CMMI-Compliant Document Structuring and Authoring

## 1. Document Control & Metadata

| Field | Value |
|---|---|
| Document ID | SKILL-CMMI-DOC-001 |
| Version | 1.0 |
| Status | Approved |
| Effective Date | 2026-05-22 |
| Classification | Configuration Item (CI) — baseline BL-DOC-001 |

### Revision History

| Version | Date | Description of Change | Author |
|---|---|---|---|
| 0.1 | 2026-05-22 | Initial draft | — |
| 1.0 | 2026-05-22 | Restructured to self-comply with own CMMI template; added Document Control, RACI, Extended ETVX, Metrics, Tailoring; removed conversational prose; added practice-area citations | — |

### Approvals

| Name | Role | Date |
|---|---|---|
| *(Process Owner / SEPG)* | Accountable | — |
| *(QA Lead)* | Consulted | — |
| *(Project Manager)* | Informed | — |

---

## 2. Introduction & Context

### 2.1 Purpose

This document defines the standard process by which an agent transforms unstructured inputs into CMMI v2.0-compliant organizational artifacts. It targets **CMMI v2.0** (the unified model maintained by the CMMI Institute / ISACA).

**CMMI v2.0 practice areas addressed:**

- **Organizational Process Definition (OPD SP 1.1):** Establishes a reusable process asset for document creation.
- **Process Quality Assurance (PQA SP 1.1):** Provides verification criteria and a quality checklist for output validation.

### 2.2 Scope

| In Scope | Out of Scope |
|---|---|
| Generation of any CMMI-compliant document type listed in `references/practice-area-mapping.md` | Level 4 (Quantitatively Managed) or Level 5 (Optimizing) practices |
| Target maturity levels: Level 2 (Managed) and Level 3 (Defined) | Non-process artifacts (source code, test scripts, deployment manifests) |

### 2.3 Audience

- AI agents executing document-generation tasks.
- Process engineers reviewing or tailoring agent-generated artifacts.
- QA auditors validating CMMI compliance of generated documents.

### 2.4 References & Definitions

| Term | Definition |
|---|---|
| CMMI v2.0 | Capability Maturity Model Integration, version 2.0 (ISACA / CMMI Institute) |
| RACI | Responsible, Accountable, Consulted, Informed — a responsibility assignment matrix |
| Extended ETVX | Entry, Inputs, Tasks, Verification, eXit, Outputs — extends IBM's classic ETVX with Inputs & Outputs |
| CI | Configuration Item — any artifact baselined under Configuration Management |
| SEPG | Software Engineering Process Group |
| OPD | Organizational Process Definition (CMMI v2.0 practice area) |
| PQA | Process Quality Assurance (CMMI v2.0 practice area) |
| CM | Configuration Management (CMMI v2.0 practice area) |

### References

| Reference | Location |
|---|---|
| Practice-area mapping — Full document-type-to-practice-area mapping. | `references/practice-area-mapping.md` |

### Referenced Skills

| Skill | Role in this Skill |
|---|---|
| `cmmi-agent-roles` | Provides role definitions referenced by RACI matrices |
| `cmmi-glue` | Governance workflows referenced in §6 Tailoring |

---

## 3. Roles and Responsibilities (RACI Matrix)

*Practice area: PQA SP 1.1 — ensures each activity has clear accountability.*

| Activity | Executing Agent¹ | EPG Member | SQA Auditor | Project Manager |
|---|---|---|---|---|
| Collect input parameters | R | A | I | C |
| Resolve practice-area mapping | R, A | C | I | I |
| Generate Document Control block | R, A | I | I | I |
| Write Introduction & Context | R, A | C | I | I |
| Build RACI matrix | R | A | C | C |
| Model workflows via Extended ETVX | R, A | C | I | I |
| Define metrics | R | A | C | I |
| Add tailoring guidelines (Level 3+) | R | A | C | I |
| Mark document as CI | R | A | I | I |
| Run quality checklist | R, A | I | C | I |
| Approve final document | I | R | R | A |
| Baseline under CM control | I | R, A | I | I |

¹ *Executing Agent* is the persona that invokes this skill. See `cmmi-agent-roles` for the persona catalog.

---

## 4. Process Architecture (Extended ETVX Model)

*Practice areas: OPD SP 1.1 — defines the standard document-generation process; CM SP 1.1 — governs artifact storage and baselining.*

The Extended ETVX structure extends the classic IBM ETVX model (Entry, Task, Verification, eXit) with two additional components — **Inputs & Sources** and **Outputs & Destinations** — to make artifact provenance and storage explicit, as required by CMMI v2.0 CM and PQA practice areas.

### E — Entry Criteria

All conditions must evaluate to true before the agent begins document generation:

- [ ] Target Document Type is specified (e.g., Software Development Plan, QA Plan, CM Procedure).
- [ ] Scope & Boundaries are defined: what is included and what is excluded.
- [ ] At least one role is identified for each RACI category (R, A, C, I).
- [ ] Raw process steps or legacy documentation are provided.
- [ ] Target CMMI Maturity Level is declared: Level 2 or Level 3.

### I — Inputs & Sources

| Input | Source | Format |
|---|---|---|
| Project name | User / project charter | Text (used to resolve output path: `projects/<project>/docs/`) |
| Target Document Type | User / project charter | Text |
| Scope & Boundaries | User / project charter | Text |
| Roles involved | Organizational chart / user input | List of role names |
| Raw process steps | User / legacy documentation | Unstructured text, bullet lists, or flowcharts |
| Target CMMI Maturity Level | User | "Level 2" or "Level 3" |
| Practice-area mapping | `references/practice-area-mapping.md` | Markdown table |

### T — Tasks / Activities

The agent executes the following steps in strict order:

1. **Parse inputs.** Extract document type, scope, roles, raw steps, and target maturity level.
2. **Resolve practice areas.** Map the target document type to CMMI v2.0 practice area(s) using `references/practice-area-mapping.md`.
3. **Generate Document Control block.** Produce Document ID, Version (v0.1 for drafts), Status, Effective Date, Revision History table, and Approvals sign-off grid.
4. **Write Introduction & Context.** Populate Purpose (cite practice areas by ID), Scope (binary applicability statements), Audience, and References & Definitions.
5. **Build RACI matrix.** Map every activity from the raw process steps to R, A, C, I roles. Enforce exactly one Accountable role per task.
6. **Model workflows using Extended ETVX.** For each operational workflow in the document:
    - Define Entry Criteria as binary conditions.
    - List Inputs & Sources with origin.
    - Describe Tasks as numbered procedural steps.
    - Specify Verification & Validation methods.
    - Define Exit Criteria as binary conditions.
    - Enumerate Outputs & Destinations with CM storage location.
7. **Define metrics.** Specify quantitative KPIs, storage location, and governance review cadence.
8. **Add tailoring guidelines** (when target level ≥ 3). Define allowed deviations and approval authority.
9. **Mark as Configuration Item.** State that the document is a CI with a baseline identifier, to be baselined under CM control once approved.
10. **Run quality checklist.** Execute all verification checks listed in the V — Verification & Validation section below.

#### Writing Constraints

| Rule | Requirement |
|---|---|
| No Conversational Prose | Use imperative, professional technical writing. Banned terms: "periodic," "as needed," "appropriate," "generally," "when ready." Use precise timeframes and absolute conditions. |
| Bidirectional Traceability | Every task traces forward to an output artifact and backward to the requirement or input that triggered it. |
| Keep it Lean | Prefer tabular matrices, bullet points, and tool hyperlinks (Jira, Confluence, Git) over block text. |
| Practice-Area Citation | Each major section cites the specific CMMI v2.0 practice area and practice it satisfies (e.g., "CM SP 1.1 — Identify Configuration Items"). |
| Inline Compliance Artifacts | Produce PlantUML diagrams, RACI matrices, and traceability entries at spec creation time — not in a separate remediation pass. |

### V — Verification & Validation

*Practice area: PQA SP 1.1 — objective evaluation of process adherence.*

Before delivering the output, the agent must verify all of the following:

- [ ] A complete Revision History block exists, starting at v1.0 (or v0.1 for drafts).
- [ ] Every task in the process workflow maps to at least one Responsible and one Accountable role in the RACI matrix.
- [ ] The RACI matrix covers every task defined in the Extended ETVX workflow (no task lacks an accountable owner).
- [ ] Entry and Exit criteria are written as binary conditions (e.g., "Approved Specification Exists," not "When the spec is mostly ready").
- [ ] A clear path is defined for metric collection and analysis.
- [ ] Metrics are tied to specific organizational objectives (required for Level 3+).
- [ ] All relevant CMMI v2.0 practice areas are cited by ID in the document sections they satisfy.
- [ ] The document is explicitly marked as a Configuration Item (CI) with a baseline identifier.
- [ ] When target maturity level is ≥ 3, tailoring guidelines are present with an identified approval authority.
- [ ] Non-conformances found during verification are escalated per `cmmi-glue` Workflow 3 (SQA Audit & Non-Compliance Escalation).

### X — Exit Criteria

- [ ] All V — Verification & Validation checks pass.
- [ ] The generated document conforms to the mandatory structure defined in this skill (sections 1–6, including the Inputs & Sources (I) row unless tailored per §6).
- [ ] The Accountable role has reviewed the output.

### O — Outputs & Destinations

| Output | Format | Destination |
|---|---|---|
| CMMI-compliant process document | Markdown | `projects/<project>/docs/process/`, baselined as a CI |
| CMMI-compliant specification | Markdown | `projects/<project>/BL/.../specifications/main.md` (at the matching hierarchy level per `config/skills/project-lifecycle/references/directory-hierarchy.md`), baselined as a CI |
| Completed quality checklist | Markdown checklist | Appended to or delivered alongside the document |

---

## 5. Measurement and Metrics

*Practice area: MPM SP 1.1 (Managing Performance and Measurement) — quantitative tracking of process effectiveness.*

| KPI | Formula | Collection Point | Organisational Objective |
|---|---|---|---|
| Checklist pass rate | (V&V items passing on first generation) / (total V&V items) × 100 | Quality checklist output | Reduce process non-conformances to < 5% per quarter (PQA) |
| Rework count | Count of revision cycles before all checks pass | Revision History table | Achieve first-pass approval rate ≥ 80% (OPD) |
| RACI coverage | (ETVX tasks with both R and A assigned) / (total ETVX tasks) × 100 | RACI matrix | Ensure 100% accountability assignment across all processes (PQA) |
| Time to approval | Elapsed time from v0.1 (first draft) to Approved status | Document Control metadata | Reduce document cycle time to support schedule adherence (PP) |

**Storage:** Record metrics in the project's metrics database or governance dashboard.

### Metric Collection Path

All document-generation metrics are collected in each document's §1 revision
history (rework count, time to approval) and in the project quality dashboard:
`projects/<project>/docs/reports/`

The SQA Auditor extracts checklist pass rate and RACI coverage from each
document's V&V output. Trends feed into `cmmi-glue` Workflow 4 (Continuous
Improvement).

**Review cadence:** The Process Owner reviews aggregated metrics at each governance cycle (minimum: once per quarter).

---

## 6. Tailoring Guidelines (Mandatory for Level 3+)

*Practice area: OPD SP 1.1 — organizational standard processes must include tailoring criteria.
All deviations follow `cmmi-glue` Workflow 1 (Tailoring Process).*

### Allowed Deviations

| Condition | Permitted Tailoring |
|---|---|
| Document scope covers a single, low-risk activity | Measurement and Metrics section (§5) may be reduced to a single KPI. |
| Fewer than 3 roles involved | RACI matrix may use a simplified 2-column (R, A) format. |
| Target maturity level is Level 2 | Tailoring Guidelines section (§6) may be omitted entirely. |
| Fast-track or prototype project | Extended ETVX may omit the Inputs & Sources (I) row when all inputs are already enumerated in Entry Criteria. |
| **Profile-P (PyCSL)** | L1–L3 specs may be `<!-- pycsl-include: source=<path> scope=<tag> -->` anchors (resolved at view time by `bin/cmmi-include-expand.py`) instead of generated prose, when the canonical source already exists (e.g. L1 includes `config/skills/csl-from-scratch/SKILL.md`; L2 SY3-Pycsl includes the `docs/pycsl-*-reference.md` triad; L3 components include sections of `pycsl-software-architecture`). L4 Module specs are auto-generated indices via `bin/cmmi-mod-index.py`. L5 Unit specs are the in-source `#@` contracts (no files generated). |

### Approval Authority

All tailoring deviations require written authorization from the **SEPG** or **QA Director** before the agent applies them. Record the deviation and its rationale in the document's Revision History.

---

*This document is a Configuration Item (CI) under baseline BL-DOC-001.
Changes require Change Control Board approval per cmmi-glue Workflow 2.*
