---
name: cmmi-glue
description: >
  Defines the four cross-role governance workflows (Tailoring, Change Control,
  SQA Audit & Non-Compliance Escalation, Continuous Improvement) that connect organizational
  roles to each other across specification levels. These are the connective
  tissues — company-wide orchestration processes that every project must trigger
  at different lifecycle stages. Use when the user asks about cross-role
  workflows, change control, tailoring processes, SQA audits, non-compliance
  escalation, process improvement loops, how agents interact, handoff protocols,
  orchestration between roles, or what happens when a requirement changes.
document_id: SKILL-CMMI-GLUE-001
version: "1.0"
status: Approved
effective_date: "2026-05-22"
baseline_id: BL-GLUE-001
cmmi_version: "2.0"
practice_areas:
  - "OPD SP 1.1 — Establish Standard Processes"
  - "PQA SP 1.1 — Objectively Evaluate Processes"
  - "CM SP 1.1 — Establish Baselines"
---

# Cross-Role Governance Workflows (Connective Tissues)

## 1. Document Control & Metadata

| Field | Value |
|---|---|
| Document ID | SKILL-CMMI-GLUE-001 |
| Version | 1.0 |
| Status | Approved |
| Effective Date | 2026-05-22 |
| Classification | Configuration Item (CI) — baseline BL-GLUE-001 |

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

*Practice areas: OPD SP 1.1 — establishes standard cross-role interaction processes; PQA SP 1.1 — governs audit and escalation workflows; CM SP 1.1 — governs change control and baselining.*

This document defines the four cross-role governance workflows that connect
organizational roles (defined in `cmmi-agent-roles`) to each other across
specification levels (defined in `cmmi-process-level`). Without these workflows,
roles operate in silos — each producing artifacts but with no defined protocol
for handoff, change propagation, compliance verification, or process evolution.

The four workflows are:

| # | Workflow | Purpose | CMMI Level |
|---|---|---|---|
| 1 | Tailoring | Adapt the standard 5-level framework to project-specific needs | Level 2+ |
| 2 | Change Control | Propagate requirement changes across all affected specification levels | Level 2+ |
| 3 | SQA Audit & Non-Compliance Escalation | Verify process compliance and handle non-conformance | Level 2+ |
| 4 | Continuous Improvement | Evolve organizational processes based on metrics evidence | Level 3+ (mandatory) |

**CMMI v2.0 practice areas addressed:**

- **Organizational Process Definition (OPD SP 1.1):** Defines reusable cross-role interaction protocols.
- **Process Quality Assurance (PQA SP 1.1):** Governs audit, NCR, and escalation workflows.
- **Configuration Management (CM SP 1.1):** Governs change control, baselining, and baseline integrity.
- **Managing Performance and Measurement (MPM SP 1.1):** Governs the continuous improvement loop.

### 2.2 Scope

| Applicable | Not applicable |
|---|---|
| Defining cross-role interaction protocols for a CMMI-compliant project | Defining individual roles (delegate to `cmmi-agent-roles` skill) |
| Generating project-specific Workflow Integration Plans | Generating specification documents (delegate to `cmmi-documents` skill) |
| Configuring tailoring, change control, audit, and improvement workflows | Classifying existing documentation (delegate to `cmmi-process-level` skill) |

### 2.3 Audience

- AI agents executing multi-role workflows that require handoff between agents.
- Process engineers designing cross-role orchestration protocols.
- Project managers configuring project governance workflows.
- SQA auditors establishing audit schedules and escalation paths.

### 2.4 References & Definitions

| Term | Definition |
|---|---|
| CCB | Change Control Board — a decision body (PM, System Architect, QA Lead) that approves/rejects change requests |
| NCR | Non-Compliance Report — a formal finding issued by SQA when a defined process is not followed |
| CAP | Corrective Action Plan — a remediation plan provided by the responsible role in response to an NCR |
| CR | Change Request — a formal request to modify a baselined specification or artifact |
| PMP | Project Management Plan — the tailored, project-specific plan derived from organizational standards |
| PAL | Process Asset Library — the organizational repository of standard processes, templates, and guidelines |
| OSSP | Organization's Set of Standard Processes |
| OPD | Organizational Process Definition (CMMI v2.0) |
| PQA | Process Quality Assurance (CMMI v2.0) |
| CM | Configuration Management (CMMI v2.0) |
| MPM | Managing Performance and Measurement (CMMI v2.0) |
| CI | Configuration Item — any artifact baselined under Configuration Management |

### References

| Reference | Location |
|---|---|
| Workflow catalog — Detailed definitions of all 4 workflows with role interaction sequences, decision gates, escalation paths, and output artifacts. | `references/workflow-catalog.md` |

### Referenced Skills

| Skill | Role in this Skill |
|---|---|
| `cmmi-agent-roles` | Defines the roles that participate in these workflows |
| `cmmi-documents` | Generates CMMI-compliant specification documents |
| `cmmi-process-level` | Classifies documentation into the 5-level hierarchy |

---

## 3. Roles and Responsibilities (RACI Matrix)

*Practice area: PQA SP 1.1 — ensures each workflow-configuration activity has clear accountability.*

| Activity | Executing Agent¹ | EPG Member | SQA Auditor | Project Manager |
|---|---|---|---|---|
| Gather project scope and CMMI maturity target | R | A | I | C |
| Select applicable workflows for the project | R, A | C | C | C |
| Configure Tailoring workflow (if applicable) | R | A | C | R |
| Configure Change Control workflow | R | A | I | C |
| Configure SQA Audit & Non-Compliance Escalation workflow | R | C | A | I |
| Configure Continuous Improvement workflow (Level 3+) | R | A | C | I |
| Generate Workflow Integration Plan | R, A | C | C | I |
| Validate workflow coverage and role assignments | R, A | I | C | I |
| Assess downstream project impact after skill version change | R | A | C | I |
| Feed pilot/import findings back into process definitions | R | A | C | I |
| Mark Workflow Integration Plan as CI | R | A | I | I |
| Approve Workflow Integration Plan | I | R | R | A |

¹ *Executing Agent* is the persona that invokes this skill. See `cmmi-agent-roles` for the persona catalog.

---

## 4. Process Architecture (Extended ETVX Model)

*Practice areas: OPD SP 1.1 — defines the workflow-configuration process; CM SP 1.1 — governs artifact baselining; PQA SP 1.1 — governs audit protocol.*

### E — Entry Criteria

All conditions must evaluate to true before the agent begins:

- [ ] Project scope is defined (what systems/products the project covers).
- [ ] Target CMMI maturity level is declared (Level 2 or Level 3).
- [ ] Organizational roles are assigned (via `cmmi-agent-roles` skill or equivalent).
- [ ] In-scope specification levels (1–5) are identified.

### I — Inputs & Sources

| Input | Source | Format |
|---|---|---|
| Project name | User / project charter | Text (used to resolve output path: `projects/<project>/docs/`) |
| Project scope description | User / project charter | Text |
| Target CMMI maturity level | User | "Level 2" or "Level 3" |
| Assigned roles | `cmmi-agent-roles` skill output or user input | Role list with level alignment |
| In-scope specification levels | `cmmi-process-level` skill output or user input | List of levels (1–5) |
| Workflow catalog | `references/workflow-catalog.md` | Markdown workflow definitions |

### T — Tasks / Activities

The agent executes the following steps in strict order:

1. **Assess project context.** Determine the project's CMMI maturity target, in-scope specification levels, and assigned roles.
2. **Select applicable workflows.** Apply the selection rules:
    - Tailoring: required for all projects (Level 2+).
    - Change Control: required for all projects (Level 2+).
    - SQA Audit & Non-Compliance Escalation: required for all projects (Level 2+).
    - Continuous Improvement: required for Level 3+; optional for Level 2.
3. **Configure each selected workflow.** For each workflow, using `references/workflow-catalog.md`:
    - Map the workflow's abstract roles to the project's assigned agents/roles.
    - Identify the trigger conditions applicable to this project.
    - Define project-specific decision gate thresholds (e.g., CCB quorum, NCR response timeframe, review cycle cadence).
    - Specify the escalation path using actual role names.
    - List the output artifacts and their CM repository destinations.
4. **Configure the Change Control cascade.** Using the Cascade Impact Matrix from `references/workflow-catalog.md`, define which roles update which specification levels when a change originates at each level.
5. **Configure the SQA Audit schedule.** Define audit checkpoints aligned to project milestones (design review, code review gate, test completion, release).
6. **Configure the Continuous Improvement cadence** (Level 3+). Define which metrics are collected, by whom, at what frequency, and the governance review cycle.
7. **Generate the Workflow Integration Plan.** Produce a single document containing:
    - List of active workflows with trigger conditions.
    - Per-workflow configuration (roles mapped, decision gates, escalation paths).
    - Change Control cascade matrix for this project.
    - SQA audit checkpoint schedule.
    - Continuous Improvement metrics and review cadence (if Level 3+).
    - Cross-workflow dependency map (how one workflow can trigger another).
8. **Validate workflow coverage.** Verify that:
    - Every assigned role appears in at least one workflow.
    - Every in-scope specification level is covered by the Change Control cascade.
    - The SQA Audit schedule covers all specification levels.
    - The escalation path terminates at a decision authority.
9. **Assess downstream project impact.** When a skill version changes (Change Control), identify projects produced under the previous version and flag them for re-validation against the updated skill's compliance checks.
10. **Feed pilot and import findings back into process definitions.** When Continuous Improvement (W4) evidence includes gaps discovered during pilot projects or imports, update the originating skill's process steps so the gap cannot recur (see skill2rag pilot → import-existing-code v1.0 → v2.0 evolution).
11. **Mark outputs as Configuration Items.** State that the Workflow Integration Plan is a CI to be baselined under CM control.

#### Writing Constraints

| Rule | Requirement |
|---|---|
| No Conversational Prose | Use imperative, professional technical writing. Banned terms: "periodic," "as needed," "appropriate," "generally," "when ready." Use precise timeframes, quorum counts, and absolute conditions. |
| Bidirectional Traceability | Every workflow step traces to the role that executes it (from `cmmi-agent-roles`) and to the specification level it affects (from `cmmi-process-level`). |
| Keep it Lean | Use sequence tables for role interactions. Use decision gate tables for approve/reject conditions. Use matrices for cascade impacts. |
| Practice-Area Citation | Cite OPD SP 1.1, PQA SP 1.1, CM SP 1.1, or MPM SP 1.1 |

### V — Verification & Validation

*Practice area: PQA SP 1.1 — objective evaluation of workflow configuration completeness.*

Before delivering the output, the agent must verify all of the following:

- [ ] A complete Revision History block exists in the Workflow Integration Plan, starting at v1.0 (or v0.1 for drafts).
- [ ] Every activity in this workflow maps to at least one Responsible and one Accountable role in the RACI matrix (§3).
- [ ] The RACI matrix covers every task defined in the Extended ETVX workflow (no task lacks an accountable owner).
- [ ] Entry Criteria were verified as true before workflow configuration began.
- [ ] All workflows required by the target CMMI maturity level are included (3 for Level 2; 4 for Level 3+).
- [ ] Every workflow has its abstract roles mapped to project-specific agents/roles.
- [ ] Every decision gate has explicit approve/reject conditions with measurable thresholds.
- [ ] The Change Control cascade matrix covers all in-scope specification levels.
- [ ] The SQA Audit schedule defines at least one checkpoint per in-scope specification level.
- [ ] The escalation path in Workflow 3 terminates at a named decision authority.
- [ ] A clear path is defined for metric collection and analysis.
- [ ] All relevant CMMI v2.0 practice areas are cited by ID in the Workflow Integration Plan.
- [ ] The Workflow Integration Plan is explicitly marked as a Configuration Item (CI) with a baseline identifier.
- [ ] When target maturity level is ≥ 3, the Continuous Improvement workflow is configured and active.

### X — Exit Criteria

- [ ] All V — Verification & Validation checks pass.
- [ ] Every selected workflow is fully configured with project-specific roles, triggers, gates, and outputs.
- [ ] The Workflow Integration Plan is generated and complete.
- [ ] The Accountable role has reviewed the output.

### O — Outputs & Destinations

| Output | Format | Destination |
|---|---|---|
| Workflow Integration Plan | Markdown | `projects/<project>/docs/reports/`, baselined as a CI |
| Per-workflow configuration summaries | Markdown tables | Embedded in Workflow Integration Plan |
| Change Control cascade matrix | Markdown table | Embedded in Workflow Integration Plan |
| SQA audit checkpoint schedule | Markdown table | Embedded in Workflow Integration Plan |
| Cross-workflow dependency map | Markdown table | Embedded in Workflow Integration Plan |

---

## 5. Measurement and Metrics

*Practice area: MPM SP 1.1 (Managing Performance and Measurement) — quantitative tracking of cross-role workflow effectiveness.*

| KPI | Formula | Collection Point | Organisational Objective |
|---|---|---|---|
| Tailoring approval cycle time | Elapsed time from Tailoring Request submission to EPG/SQA approval | Tailoring workflow | Maintain controlled process adaptation rate < 10% per quarter (OPD SP 1.1) |
| Change request cycle time | Elapsed time from CR submission to new baseline lock | Change Control workflow | Reduce CR processing time to support project velocity (CM SP 1.1) |
| NCR resolution rate | (NCRs closed with verified corrective action within response timeframe) / (total NCRs) × 100 | SQA Audit workflow | Close ≥ 90% of NCRs within one audit cycle (PQA SP 1.1) |
| NCR escalation rate | (NCRs escalated to upper management / EPG) / (total NCRs) × 100 | SQA Audit workflow | Keep escalated NCRs at ≤ 10% of total NCRs per quarter (PQA SP 1.1) |
| Process improvement actions implemented | Count of standard process updates derived from metrics evidence | Continuous Improvement workflow | Implement ≥ 75% of approved improvements per quarter (MPM SP 1.1) |
| Workflow coverage | (assigned roles appearing in ≥ 1 active workflow) / (total assigned roles) × 100 | Workflow Integration Plan | Maintain 100% role coverage in active workflows per project (OPD SP 1.1) |

**Storage:** Record metrics in the project's metrics database or governance dashboard.

### Metric Collection Path

All governance metrics are collected in workflow output artifacts stored under:
`projects/<project>/docs/process/`

- Tailoring approval cycle time: captured in Tailoring Request artifacts.
- Change request cycle time: captured in Change Request / baseline records.
- NCR resolution rate and NCR escalation rate: captured in SQA audit reports
  under `projects/<project>/docs/audits/`.
- Process improvement actions implemented: tracked in Process Performance Reports.
- Workflow coverage: captured in Workflow Integration Plan role-to-workflow mapping tables.

The Metrics Analyst aggregates governance metrics quarterly. Workflow 4
(Continuous Improvement) consumes these as primary input (see
`references/workflow-catalog.md` Workflow 4).

**Review cadence:** The Process Owner reviews aggregated metrics at each governance cycle (minimum: once per quarter).

---

## 6. Tailoring Guidelines (Mandatory for Level 3+)

*Practice area: OPD SP 1.1 — organizational standard processes must include tailoring criteria.*

### Allowed Deviations

| Condition | Permitted Tailoring |
|---|---|
| Project duration < 3 months with low risk | Tailoring workflow (Workflow 1) may use a simplified single-approval gate (EPG only, without separate SQA review). |
| Fewer than 3 roles assigned | Change Control CCB may be reduced to 2 members (PM + one technical role). |
| Target maturity level is Level 2 | Continuous Improvement workflow (Workflow 4) may be omitted entirely. |
| Single-agent project | SQA Audit workflow (Workflow 3) may use self-review with documented checklist instead of independent audit. Note: this reduces CMMI compliance and must be justified. |
| Project has no external change requests | Change Control workflow (Workflow 2) may be simplified to internal-only change tracking without formal CCB meetings. Decision authority shifts to PM + CM. |
| **Profile-P (PyCSL)** | Single-developer CCB: CCB is the developer + the changed file itself; approval = the commit; CR-ID = commit SHA; no separate ticket system. SQA Audit (Workflow 3) uses self-review per `cmmi-coherency-audit` Profile-P scope + the new `bin/cmmi-audit.sh` gate. Continuous Improvement (Workflow 4) feeds from existing `metrics/` outputs via `bin/cmmi-metrics-ingest.py` (no separate `metrics-store.json` source). Workflow 3 binding for SY3-Pycsl + SY6-PycslLib L3-ceiling escalations: `coordinator.py` exit 72/73 → `agent-meta-monitor.py` → `agent-feature-supervisor.py` → human review. The L3-ceiling fallback (`# cite:_note:` line in an annotated stub) IS the Workflow 3 signal. |

### Approval Authority

All tailoring deviations require written authorization from the **SEPG** or **QA Director** before the agent applies them. Record the deviation and its rationale in the Workflow Integration Plan's Revision History.

---

*This document is a Configuration Item (CI) under baseline BL-GLUE-001.
Changes require Change Control Board approval per cmmi-glue Workflow 2.*
