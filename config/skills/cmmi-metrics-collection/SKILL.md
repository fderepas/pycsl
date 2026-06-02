---
name: cmmi-metrics-collection
description: >
  Aggregates §5 KPIs from all KPI source skills across all project instances into a
  unified time-series store. Extracts skill metrics, normalizes records,
  computes organizational baselines, and publishes metric assets that support
  Organizational Process Performance and quantitative project management. Use
  when the user asks to collect CMMI metrics, aggregate cross-project KPIs,
  build process-performance baselines, populate a metrics store, or prepare
  quantitative data for organizational analysis.
document_id: SKILL-CMMI-METR-001
version: "1.0"
status: Approved
effective_date: "2026-05-22"
baseline_id: BL-METR-001
cmmi_version: "2.0"
practice_areas:
  - "MPM SP 1.1 — Align measurement and performance objectives"
  - "OPP SP 1.1 — Establish process-performance baselines"
---

# CMMI Metrics Collection and Baseline Assembly

## 1. Document Control & Metadata

| Field | Value |
|---|---|
| Document ID | SKILL-CMMI-METR-001 |
| Version | 1.0 |
| Status | Approved |
| Effective Date | 2026-05-22 |
| Baseline ID | BL-METR-001 |
| CMMI Version | 2.0 |

### Revision History

| Version | Date | Author | Change Summary |
|---|---|---|---|
| 1.0 | 2026-05-22 | Agent (EPG) | Initial release — unified KPI extraction, normalization, and baseline assembly skill |

### Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| Accountable — EPG Lead | _(pending)_ | | |
| Responsible — Metrics Analyst | _(pending)_ | | |
| Consulted — SQA Auditor | _(pending)_ | | |
| Informed — Configuration Manager | _(pending)_ | | |

---

## 2. Introduction & Context

### Purpose

*Practice areas: MPM SP 1.1 — aligns enterprise KPI collection with measurement objectives; OPP SP 1.1 — establishes the data foundation for organizational process-performance baselines.*

This skill collects, normalizes, and stores KPIs from all KPI source skills across
project instances into a unified time-series format. The resulting records
support Organizational Process Performance baselines and provide the data feed
consumed by quantitative management activities.

### Scope

| In Scope | Out of Scope |
|---|---|
| Extracting §5 KPIs from the 9 source skills in `config/skills/` (6 CMMI-structured skills: `cmmi-agent-roles`, `cmmi-coherency-audit`, `cmmi-documents`, `cmmi-glue`, `cmmi-process-level`, `spin-modeling`; plus 3 supporting framework skills: `communication`, `project-lifecycle`, `import-existing-code`) | Statistical process control execution delegated to `cmmi-quantitative-mgmt` |
| Normalizing KPI data into JSON time-series records | SPC chart generation |
| Storing per-project metric histories and organization-level baselines | Root cause analysis |
| Computing running baselines (mean, σ) across project instances | Manual interpretation of corrective actions |

### Audience

- Metrics Analysts executing collection runs.
- EPG Leads reviewing organizational baselines.
- SQA Auditors verifying extraction integrity and report completeness.
- Configuration Managers maintaining controlled metric storage locations.
- Quantitative management consumers reading baseline outputs.

### References & Definitions

| Term | Definition |
|---|---|
| KPI | A quantitative indicator declared in a skill's §5 Measurement and Metrics section |
| Time-series record | One normalized JSON object containing project, date, skill, KPI, value, unit, phase, and run |
| Baseline | A running mean and standard deviation computed for one KPI across all collected records |
| Insufficient for baseline | Status assigned to any KPI with fewer than 3 collected data points |

### References

| Reference | Location |
|---|---|
| Workflow 4 Skill Metric Sources | `config/skills/cmmi-glue/references/workflow-catalog.md` |
| Agent-role KPI definitions | `config/skills/cmmi-agent-roles/SKILL.md` §5 |
| Coherency-audit KPI definitions | `config/skills/cmmi-coherency-audit/SKILL.md` §5 |
| Document KPI definitions | `config/skills/cmmi-documents/SKILL.md` §5 |
| Governance KPI definitions | `config/skills/cmmi-glue/SKILL.md` §5 |
| Process-level KPI definitions | `config/skills/cmmi-process-level/SKILL.md` §5 |
| Communication KPI definitions | `config/skills/communication/SKILL.md` §5 |
| Lifecycle KPI definitions | `config/skills/project-lifecycle/SKILL.md` §5 |

### Referenced Skills

| Skill | Role in this Skill |
|---|---|
| `cmmi-agent-roles` | Source of role-assignment KPIs |
| `cmmi-coherency-audit` | Source of framework coherency KPIs |
| `cmmi-documents` | Source of document-generation KPIs |
| `cmmi-glue` | Source of governance KPIs and Workflow 4 collection paths |
| `cmmi-process-level` | Source of classification and gap KPIs |
| `communication` | Source of communication-flow KPIs |
| `import-existing-code` | Source of import process KPIs (retro-spec coverage, test pass rate, compliance audit pass rate, traceability completeness) |
| `spin-modeling` | Source of formal-verification KPIs (state space size, property coverage, counter-example resolution rate) |
| `project-lifecycle` | Source of lifecycle execution KPIs |
| `cmmi-quantitative-mgmt` | Downstream consumer of `projects/<project>/docs/metrics/org-baselines.json`; not a KPI source |

> **Source skill count rationale:** 6 CMMI-structured skills (`cmmi-agent-roles`,
> `cmmi-coherency-audit`, `cmmi-documents`, `cmmi-glue`, `cmmi-process-level`,
> `spin-modeling`) plus 3 supporting framework skills (`communication`,
> `project-lifecycle`, `import-existing-code`) are KPI sources.
> `cmmi-metrics-collection` (this skill) is excluded because it is the
> collector, not a source. `cmmi-quantitative-mgmt` is excluded because it
> consumes baselines produced by this skill rather than contributing raw KPIs.

---

## 3. RACI Matrix

*Practice areas: MPM SP 1.1 — assigns ownership for KPI collection; OPP SP 1.1 — assigns accountability for baseline construction.*

| Task | Activity | Metrics Analyst | EPG Lead | SQA Auditor | Configuration Manager |
|---|---|---|---|---|---|
| A1 | Enumerate KPI catalog from all source skills | R | A | C | I |
| A2 | Scan project collection paths from Workflow 4 | R | A | C | I |
| A3 | Extract KPI values from source artifacts | R | A | C | I |
| A4 | Normalize records into the approved JSON schema | R | A | C | I |
| A5 | Append per-project metrics stores | R | A | — | I |
| A6 | Compute organization-level baselines and sufficiency flags | R | A | C | I |
| A7 | Verify outputs and file the metrics collection report | R | A | C | I |

---

## 4. Process Architecture (Extended ETVX Model)

*Practice areas: MPM SP 1.1 — defines the collection workflow; OPP SP 1.1 — defines how baseline-ready data is assembled and verified.*

### E — Entry Criteria

All conditions must evaluate to true before starting collection:

- [ ] At least 1 project exists under `projects/` with completed V-cycle phases that produced §5 metric artifacts.
- [ ] The skill library at `config/skills/` contains the referenced source skills with populated §5 Measurement and Metrics sections.

### I — Inputs & Sources

| Input | Source | Format |
|---|---|---|
| Source skill metric definitions | §5 of the 9 source skills listed in §2 Referenced Skills | Markdown |
| Workflow 4 Skill Metric Sources table | `config/skills/cmmi-glue/references/workflow-catalog.md` | Markdown table |
| Project instances | `projects/<project>/` | Directory tree |
| Skill-specific metric artifacts | Audit reports, gap reports, role-assignment reports, message logs, governance records | Markdown, JSON, text |
| Existing metrics store (optional) | `projects/<project>/docs/metrics/metrics-store.json` | JSON |
| Existing org baselines (optional) | `projects/<project>/docs/metrics/org-baselines.json` | JSON |

### T — Tasks / Activities

1. **Enumerate KPI definitions.** Inspect §5 of the 9 source skills listed in §2 Referenced Skills and build a master KPI catalog containing skill name, KPI name, unit, collection path, and organizational objective.
2. **Scan project collection paths.** For each project in `projects/`, resolve the skill-specific collection paths declared in the Workflow 4 Skill Metric Sources table in `config/skills/cmmi-glue/references/workflow-catalog.md`.
3. **Extract KPI values.** Read collection-path artifacts and extract KPI values from audit reports, gap reports, role-assignment reports, message logs, governance records, and related evidence files.
4. **Normalize time-series records.** Convert each extracted data point to the approved JSON schema:

```json
{"project": "...", "collected_at": "YYYY-MM-DD", "skill": "...", "kpi": "...", "value": 0, "unit": "...", "phase": "...", "run": 0}
```

5. **Append per-project stores.** Write each normalized record to `projects/<project>/docs/metrics/metrics-store.json`. Create the file first if it does not yet exist, then append the new record set without deleting prior history.
6. **Compute running baselines.** Aggregate each KPI across all projects and compute running mean and standard deviation. Write the results to `projects/<project>/docs/metrics/org-baselines.json` and mark any KPI with fewer than 3 data points as `"insufficient for baseline"`.
7. **File the collection report.** Produce `projects/<project>/docs/reports/metrics-collection-<NNN>.md` summarizing scanned sources, extracted record counts, baseline status, insufficient-data flags, and exceptions.

#### Writing Constraints

| Rule | Requirement |
|---|---|
| Deterministic extraction | Use declared collection paths and explicit artifact evidence for every KPI value. |
| Schema conformance | Every record uses the exact JSON field set defined in Task 4. |
| Traceability | Every baseline value traces back to project-level records and source artifacts. |
| Sufficiency rule | Any KPI with fewer than 3 data points is marked `insufficient for baseline` without exception. |

### V — Verification & Validation

*Practice areas: MPM SP 1.1 — confirms complete KPI acquisition; OPP SP 1.1 — confirms baseline integrity.*

- [ ] The KPI catalog covers §5 metrics from the 9 source skills listed in §2 Referenced Skills.
- [ ] Every project under `projects/` was evaluated against the Workflow 4 Skill Metric Sources table.
- [ ] Every extracted record conforms to the approved JSON schema.
- [ ] Each `projects/<project>/docs/metrics/metrics-store.json` file is valid JSON and contains only normalized time-series records.
- [ ] `projects/<project>/docs/metrics/org-baselines.json` contains mean and standard deviation for every KPI with at least 3 data points (unless Profile S is active per §6).
- [ ] Every KPI with fewer than 3 data points is marked `insufficient for baseline`.
- [ ] A metrics collection report exists for each project processed in the run.

### X — Exit Criteria

- [ ] Metrics store exists with valid time-series data for every extractable KPI.
- [ ] Org baselines are computed for all KPIs with at least 3 data points (unless Profile S is active per §6).
- [ ] A summary report is filed for every project processed in the run.
- [ ] Non-conformances found during verification are escalated per `cmmi-glue` Workflow 3 (SQA Audit & Non-Compliance Escalation).
- [ ] All V — Verification & Validation checks pass.

### O — Outputs & Destinations

| Output | Format | Destination |
|---|---|---|
| Per-project metrics store | JSON | `projects/<project>/docs/metrics/metrics-store.json` |
| Org baselines | JSON | `projects/<project>/docs/metrics/org-baselines.json` |
| Metrics collection report | Markdown | `projects/<project>/docs/reports/metrics-collection-<NNN>.md` |

---

## 5. Measurement and Metrics

*Practice areas: MPM SP 1.1 — monitors collection performance; OPP SP 1.1 — monitors baseline readiness.*

| KPI | Formula | Collection Point | Organisational Objective |
|---|---|---|---|
| Collection completeness | (defined KPIs with at least 1 data point / total defined KPIs) × 100 | `projects/<project>/docs/reports/metrics-collection-<NNN>.md` | Reach 100% representation of defined CMMI KPIs in the organizational store |
| Baseline coverage | (defined KPIs with at least 3 data points / total defined KPIs) × 100 | `projects/<project>/docs/reports/metrics-collection-<NNN>.md` | Expand baseline-ready KPI coverage until every defined KPI has a valid baseline |
| Data staleness | Maximum age in days of the latest data point for any KPI stream | `projects/<project>/docs/reports/metrics-collection-<NNN>.md` | Keep the oldest latest KPI value at 30 days or less |

### Metric Collection Path

The control record for this skill's meta-metrics is:
`projects/<project>/docs/reports/metrics-collection-<NNN>.md`

Supporting evidence is stored in `projects/<project>/docs/metrics/metrics-store.json`
and `projects/<project>/docs/metrics/org-baselines.json`.

### Governance Review Cadence

The Metrics Analyst updates the metrics store after each collection run. The EPG
Lead reviews `projects/<project>/docs/metrics/org-baselines.json` on the first business day of
each month and after any change to a §5 KPI definition in the skill library.
The SQA Auditor samples one metrics collection report during that monthly
review.

---

## 6. Tailoring Guidelines

*Practice area: OPP SP 1.1 — tailoring preserves baseline comparability. All deviations follow `cmmi-glue` Workflow 1 (Tailoring Process).*

| Deviation | Conditions for Approval | Approval Authority |
|---|---|---|
| Profile S | Collect Level 1 and Level 2 KPI sources only; skip cross-project baselines | EPG Lead |
| Profile M | Collect all KPIs; baselines may remain unpublished until at least 3 projects contribute data | EPG Lead |
| Profile L | Full KPI collection and org baselines are required | No deviation — full run required |
| **Profile-P (PyCSL)** | Canonical metrics source is the existing `metrics/` tree (`metrics/logs/`, `metrics/monitor/`, `metrics/evaluator/`, `metrics/reviewer/`); normalised into per-system snapshots by `bin/cmmi-metrics-ingest.py`. Per-system KPIs include: file count, LOC, `#@` contract line count, L3-ceiling note count, doc-coherency exit, log volume. Output store at `projects/pycsl/docs/metrics/metrics-store.json` references source via `source_uri` (never duplicates). PyCSL-specific KPIs: L3-ceiling rate per system, Reconciliator escalation rate (Workflow-3 events / proof failures), spec-mirror drift events (C8 failures). Agent-ecosystem L4 KPIs (inter-agent loop efficiency, reconciliation diagnostic accuracy, Rocq proof difficulty, feature-rollout gate/acceptance/delegation rates) are defined in [`references/agent-loop-kpis.md`](references/agent-loop-kpis.md); sourced from the per-run summaries (`metrics/run-summary/`, `metrics/feature-supervisor/<slug>/run-summary.json`) and landed under `global.agent_loop_kpis`. Baselines reset when `bin/cmmi-metrics-ingest.py --weekly` has ≥8 snapshots. | Developer (single-developer CCB) |

All approved deviations must be recorded in the metrics collection report with
the selected profile, omitted sources, and approval reference from `cmmi-glue`
Workflow 1.

---

*This document is a Configuration Item (CI) under baseline BL-METR-001.
Changes require Change Control Board approval per `cmmi-glue` Workflow 2.*
