---
name: cmmi-agent-roles
description: >
  Defines agent personas for a CMMI-compliant project by mapping organizational
  roles (Governance and V-Cycle Engineering layers) to agent persona files.
  Selects applicable roles based on project scope and CMMI maturity target,
  generates ready-to-use persona markdown files for config/agents/, and
  produces a project RACI matrix ensuring every specification level has a
  Specifier, Governance role, and Verifier. Use when the user asks to define
  agent roles, create agent personas, assign roles to agents, set up an
  agent team, build a RACI for agents, determine who does what at each
  specification level, figure out who should do what, who owns what, what
  roles are needed, staff a project, design team structure, or decide which
  agent handles which level.
document_id: SKILL-CMMI-ROLE-001
version: "1.0"
status: Approved
effective_date: "2026-05-22"
baseline_id: BL-ROLE-001
cmmi_version: "2.0"
practice_areas:
  - "OPD SP 1.1 — Establish Standard Processes"
  - "PQA SP 1.1 — Objectively Evaluate Processes"
  - "PLAN SP 1.1 — Establish Estimates"
---

# CMMI Agent Role Definition and Persona Generation

## 1. Document Control & Metadata

| Field | Value |
|---|---|
| Document ID | SKILL-CMMI-ROLE-001 |
| Version | 1.0 |
| Status | Approved |
| Effective Date | 2026-05-22 |
| Classification | Configuration Item (CI) — baseline BL-ROLE-001 |

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

*Practice area: OPD SP 1.1 — establishes a standard process for agent role definition and persona generation.*

This document defines the process by which an agent selects organizational roles
for a project, maps them to specification levels (1–5), and generates agent
persona files. The two role layers are:

| Layer | Scope | Roles |
|---|---|---|
| Governance | Cross-cutting CMMI process oversight | EPG/SEPG, Configuration Manager, SQA Auditor, Metrics Analyst |
| Engineering | V-Cycle product execution, levels 1–5 | Business Analyst/PO, System Architect, Technical Lead, Software Engineer, Test Engineer, Reconciliator |

**CMMI v2.0 practice areas addressed:**

- **Organizational Process Definition (OPD SP 1.1):** Defines a standard role-assignment and persona-generation process.
- **Process Quality Assurance (PQA SP 1.1):** Ensures every specification level has accountable roles assigned.
- **Planning (PLAN SP 1.1):** Supports project staffing and responsibility allocation.

### 2.2 Scope

| In Scope | Out of Scope |
|---|---|
| Selecting organizational roles for agent personas based on project scope and CMMI maturity target | Human HR processes, org chart definition, or personnel management |
| Generating agent persona `.md` files for `config/agents/` | Generating CMMI-compliant specification documents (delegate to `cmmi-documents` skill) |
| Producing a project RACI matrix for role-to-level coverage | Classifying existing documentation (delegate to `cmmi-process-level` skill) |

### 2.3 Audience

- AI agents executing role-definition and team-setup tasks.
- Process engineers designing multi-agent workflows.
- Project managers allocating agent responsibilities across specification levels.

### 2.4 References & Definitions

| Term | Definition |
|---|---|
| Governance Role | A cross-cutting role focused on CMMI process oversight, not product creation |
| Engineering Role | A V-Cycle role aligned to a specific specification level, focused on product execution |
| Persona File | A markdown file in `config/agents/` defining an agent's identity, responsibilities, and scope |
| V-Cycle | The V-Model lifecycle: top-down specification, bottom-up verification |
| Specifier | The Engineering role responsible for creating specifications at a given level |
| Verifier | The Engineering role responsible for testing/validating at a given level |
| OPD | Organizational Process Definition (CMMI v2.0) |
| PQA | Process Quality Assurance (CMMI v2.0) |
| PLAN | Planning (CMMI v2.0) |
| CI | Configuration Item — any artifact baselined under Configuration Management |
| CCB | Change Control Board |

### Abstract Role Aliases

The following abstract role aliases are recognized as valid RACI column headers.
Each alias resolves to one or more concrete personas from `config/agents/` at
invocation time.

| Alias | Semantics | Used By |
|---|---|---|
| Executing Agent | The persona that invokes the skill; varies by context. The invoking skill's Referenced Skills table identifies which persona triggers each invocation. | `cmmi-agent-roles`, `cmmi-documents`, `cmmi-glue`, `cmmi-process-level` |
| Sending Agent | The persona initiating a communication message. Binds to any persona from the agent catalog at send time. | `communication` |
| Receiving Agent | The persona receiving a communication message. Binds to any persona from the agent catalog at receive time. | `communication` |
| Agent (any) | Any persona performing shared infrastructure tasks (e.g., queue maintenance). | `communication` |
| All stakeholders | Broadcast notification target — not a single persona. All personas with an interest in the outcome receive an informational notification. | `cmmi-coherency-audit`, `project-lifecycle` |
| All agents | Broadcast notification target for runtime events — semantically equivalent to "All stakeholders" but scoped to agent-to-agent notifications. | `communication` |
| Reconciliator | The persona responsible for diagnosing test failures and routing faults at a given V-model level. Binds to `reconciliation-agent` persona. | `project-lifecycle` |

### References

| Reference | Location |
|---|---|
| cmmi-documents skill — Use to generate CMMI-compliant specification documents. | `config/skills/cmmi-documents/SKILL.md` |
| cmmi-process-level skill — Use to classify existing documentation into specification levels. | `config/skills/cmmi-process-level/SKILL.md` |
| Role catalog — Complete role definitions with selection criteria and level mappings. | `references/role-catalog.md` |
| Persona template — Template for generating agent persona files. | `references/persona-template.md` |

### Referenced Skills

| Skill | Role in this Skill |
|---|---|
| `cmmi-documents` | Generate CMMI-compliant specification documents |
| `cmmi-process-level` | Classify existing documentation into specification levels |

---

## 3. Roles and Responsibilities (RACI Matrix)

*Practice area: PQA SP 1.1 — ensures each role-definition activity has clear accountability.*

| Activity | Executing Agent¹ | EPG Member | SQA Auditor | Project Manager |
|---|---|---|---|---|
| Gather project scope and CMMI maturity target | R | A | I | C |
| Identify in-scope specification levels | R, A | C | I | C |
| Select applicable Engineering roles per level | R, A | C | I | I |
| Select applicable Governance roles per maturity target | R, A | C | C | I |
| Select Reconciliation role for levels using recursive execution | R, A | C | I | I |
| Generate agent persona files | R, A | C | I | I |
| Build project RACI matrix (role-to-level) | R, A | C | C | I |
| Validate coverage (Specifier + Governance + Verifier + Reconciliation per level) | R, A | I | C | I |
| Produce role-assignment report | R, A | I | C | I |
| Approve role assignments | I | R | R | A |

¹ *Executing Agent* is the persona that invokes this skill. See `cmmi-agent-roles` for the persona catalog.

---

## 4. Process Architecture (Extended ETVX Model)

*Practice areas: OPD SP 1.1 — defines the role-assignment workflow; PLAN SP 1.1 — governs project staffing; PQA SP 1.1 — ensures role coverage.*

### E — Entry Criteria

All conditions must evaluate to true before the agent begins:

- [ ] Project scope is defined (what systems/products the project covers).
- [ ] Target specification levels (1–5) are identified or determinable from scope.
- [ ] Target CMMI maturity level is declared (Level 2 or Level 3), or explicitly marked as not applicable per §6.
- [ ] The agent persona file convention is understood (`config/agents/*.md`).

### I — Inputs & Sources

| Input | Source | Format |
|---|---|---|
| Project name | User / project charter | Text (used to resolve output path: `projects/<project>/docs/`) |
| Project scope description | User / project charter | Text |
| Target specification levels | User or derived from `cmmi-process-level` skill | List of levels (1–5) |
| Target CMMI maturity level | User | "Level 2" or "Level 3" |
| Existing team structure (optional) | User / org chart | List of current roles |
| Role catalog | `references/role-catalog.md` | Markdown role definitions |
| Persona template | `references/persona-template.md` | Markdown template |

### T — Tasks / Activities

The agent executes the following steps in strict order:

1. **Assess project scope.** Determine which specification levels (1–5) are in scope based on the project description. If unclear, invoke the `cmmi-process-level` skill to classify existing documentation and derive in-scope levels.
2. **Select Engineering roles.** For each in-scope level, select the Primary Specifier and Verifier from `references/role-catalog.md` using the selection criteria. Apply the Test Engineer specialization rule: generate separate personas per level when 3+ levels are in scope; generate a single multi-level persona when 1–2 levels are in scope.
3. **Select Reconciliation role.** If the project uses recursive level-based execution (2+ specification levels in scope), include the Reconciliator. The Reconciliator is a single cross-cutting persona operating at all in-scope levels.
4. **Select Governance roles.** Based on the target CMMI maturity level, select applicable Governance roles from `references/role-catalog.md` using the selection criteria. All four Governance roles are required for Level 3+; EPG, CM, and SQA are required for Level 2.
5. **Validate coverage.** Apply the Coverage Validation Rule from `references/role-catalog.md` §4:
    - Every in-scope level has exactly one Primary Specifier.
    - Every in-scope level has at least one Governance role.
    - Every in-scope level has at least one Verifier.
    - Every in-scope level using recursive execution has Reconciliation assigned.
    - All Governance roles required by the CMMI maturity target are assigned.
    - No orphan roles (no role without a corresponding in-scope level).
6. **Generate persona files.** For each selected role, produce an agent persona `.md` file using the template from `references/persona-template.md`. Populate all required fields: name, role, layer, level_alignment, persona description, responsibilities, level scope, skills, and constraints.
7. **Build project RACI matrix.** Produce a table mapping every selected role to specification-level activities (Specify, Govern, Verify, Reconcile) with RACI assignments.
8. **Produce role-assignment report.** Generate a summary containing:
    - List of selected roles with level alignment.
    - Project RACI matrix.
    - Coverage validation results (pass/fail per level).
    - List of generated persona files with paths.

#### Writing Constraints

| Rule | Requirement |
|---|---|
| No Conversational Prose | Persona descriptions use second-person imperative ("You are…"). No vague terms. Every responsibility is a concrete action. |
| Bidirectional Traceability | Every persona file traces to a role in `references/role-catalog.md` and to the specification level(s) it serves. |
| Keep it Lean | Use tables for the RACI matrix, coverage validation, and role summaries. Use bullet points for responsibilities and constraints. |
| Practice-Area Citation | Cite OPD SP 1.1, PQA SP 1.1, or PLAN SP 1.1 in the role-assignment report and in each persona's purpose statement. |

### V — Verification & Validation

*Practice area: PQA SP 1.1 — objective evaluation of role-assignment completeness.*

Before delivering the output, the agent must verify all of the following:

- [ ] A complete Revision History block exists in the role-assignment report, starting at v1.0 (or v0.1 for drafts).
- [ ] Every activity in this workflow maps to at least one Responsible and one Accountable role in the RACI matrix (§3).
- [ ] The RACI matrix covers every task defined in the Extended ETVX workflow (no task lacks an accountable owner).
- [ ] Entry Criteria were verified as true before role selection began.
- [ ] Every in-scope specification level has a Primary Specifier, at least one Governance role, at least one Verifier, and (when using recursive execution) a Reconciliation role assigned.
- [ ] All Governance roles required by the target CMMI maturity level are included.
- [ ] Every generated persona file follows the template from `references/persona-template.md` (all required fields populated).
- [ ] No persona contains vague or conversational language.
- [ ] A clear path is defined for metric collection and analysis.
- [ ] All relevant CMMI v2.0 practice areas are cited by ID in the role-assignment report.
- [ ] The role-assignment report and persona files are marked as Configuration Items (CIs) with baseline identifiers.
- [ ] When target maturity level is ≥ 3, tailoring guidelines are noted.
- [ ] Non-conformances found during verification are escalated per `cmmi-glue` Workflow 3 (SQA Audit & Non-Compliance Escalation).

### X — Exit Criteria

- [ ] All V — Verification & Validation checks pass.
- [ ] Every in-scope specification level passes coverage validation.
- [ ] All persona files are generated and written to `config/agents/`.
- [ ] The project RACI matrix is complete.
- [ ] The Accountable role has reviewed the output.

### O — Outputs & Destinations

| Output | Format | Destination |
|---|---|---|
| Agent persona files | Markdown (one per role) | `config/agents/<role-slug>.md` |
| Project RACI matrix | Markdown table | Role-assignment report |
| Coverage validation results | Markdown table | Role-assignment report |
| Role-assignment report | Markdown | `projects/<project>/docs/reports/`, baselined as a CI |

---

## 5. Measurement and Metrics

*Practice area: MPM SP 1.1 (Managing Performance and Measurement) — quantitative tracking of role-assignment effectiveness.*

| KPI | Formula | Collection Point | Organisational Objective |
|---|---|---|---|
| Role coverage rate | (in-scope levels with Specifier + Governance + Verifier) / (total in-scope levels) × 100 | Coverage validation output | Ensure every specification level has accountable ownership — zero unowned levels (PQA) |
| Persona completeness | (required template fields populated across all personas) / (total required fields) × 100 | Persona file audit | Maintain standardized agent definitions to support process repeatability (OPD) |
| Orphan role count | Count of roles assigned without a corresponding in-scope level | Coverage validation output | Eliminate wasted resources by ensuring every role maps to active project scope (PP) |
| Governance compliance | (required Governance roles present) / (required Governance roles for target maturity) × 100 | Role selection output | Achieve 100% governance role assignment per CMMI maturity target (PQA) |

**Storage:** Record metrics in the project's metrics database or governance dashboard.

### Metric Collection Path

All role-assignment metrics are collected in:
`projects/<project>/docs/reports/role-assignment-report.md`

The role-assignment report embeds coverage rate, persona completeness, and
governance compliance data. The EPG Lead reviews metrics after each
role-assignment run. Trends feed into `cmmi-glue` Workflow 4 (Continuous
Improvement).

**Review cadence:** The Process Owner reviews aggregated metrics at each governance cycle (minimum: once per quarter).

---

## 6. Tailoring Guidelines (Mandatory for Level 3+)

*Practice area: OPD SP 1.1 — organizational standard processes must include tailoring criteria.
All deviations follow `cmmi-glue` Workflow 1 (Tailoring Process).*

### Allowed Deviations

| Condition | Permitted Tailoring |
|---|---|
| Project covers only 1–2 specification levels | Test Engineer may be a single multi-level persona instead of separate per-level personas. |
| Single-agent project (one agent handles all roles) | Generate a single "Generalist Agent" persona that combines Specifier and Verifier responsibilities; Governance constraints still apply. |
| No CMMI maturity target specified | Governance roles may be omitted; generate Engineering roles only. Note the omission in the role-assignment report. |
| Target maturity level is Level 2 | Metrics Analyst role may be omitted. |
| Fewer than 3 distinct roles needed | Project RACI matrix may use a simplified 2-column (R, A) format. |
| **Profile-P (PyCSL)** | The developer plays all three roles (Specifier / Verifier / Reconciliator) serially with role hat-switching recorded in commits (`role: specifier\|verifier\|reconciliator` tag). Per-system role binding is the corresponding `BL/SY<N>-<Name>/specifications/agents/{specifier,verifier,reconciliator}.md` persona stub — that file references the concrete agent script (e.g. `agent-stdlib-annotate.py`, `coordinator.py`, `agent-feature-supervisor.py`). The 8 `pycsl-*` domain skills are exempt from §1–§6 retrofit (per `should-we-cmmi-or-not.md` §6 Rule 3). |

### Approval Authority

All tailoring deviations require written authorization from the **SEPG** or **QA Director** before the agent applies them. Record the deviation and its rationale in the role-assignment report's Revision History.

---

*This document is a Configuration Item (CI) under baseline BL-ROLE-001.
Changes require Change Control Board approval per cmmi-glue Workflow 2.*
