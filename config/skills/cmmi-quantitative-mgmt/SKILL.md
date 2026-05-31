---
name: cmmi-quantitative-mgmt
description: >
  Implements Organizational Process Performance (OPP) and Quantitative Project
  Management (QPM) for CMMI Level 4 by computing process performance baselines,
  setting statistical control limits, generating SPC control charts, detecting
  out-of-control signals, and producing QPM reports with quantitative
  objectives and improvement recommendations. Use when the user asks to
  compute baselines, generate SPC charts, detect out-of-control signals, build
  quantitative prediction models from historical KPI data, or prepare QPM
  reports.
document_id: SKILL-CMMI-QPM-001
version: "1.0"
status: Approved
effective_date: "2026-05-22"
baseline_id: BL-QPM-001
cmmi_version: "2.0"
practice_areas:
  - "OPP SP 1.1"
  - "OPP SP 1.2"
  - "OPP SP 1.3"
  - "QPM SP 1.1"
  - "QPM SP 1.2"
  - "QPM SP 1.3"
  - "QPM SP 1.4"
---

# Quantitative Management (OPP + QPM)

## 1. Document Control & Metadata

| Field | Value |
|---|---|
| Document ID | SKILL-CMMI-QPM-001 |
| Version | 1.0 |
| Status | Approved |
| Effective Date | 2026-05-22 |
| Baseline ID | BL-QPM-001 |
| CMMI Version | 2.0 |

### Revision History

| Version | Date | Author | Change Summary |
|---|---|---|---|
| 1.0 | 2026-05-22 | Agent (EPG) | Initial release — OPP and QPM skill for baselines, control limits, SPC charts, and out-of-control detection |

### Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| Accountable — EPG Lead | _(pending)_ | | |
| Responsible — Metrics Analyst | _(pending)_ | | |
| Consulted — SQA Auditor | _(pending)_ | | |

---

## 2. Introduction & Context

### Purpose

*Practice areas: OPP SP 1.1, OPP SP 1.2, OPP SP 1.3, QPM SP 1.1, QPM SP 1.2, QPM SP 1.3, and QPM SP 1.4 — quantitative baseline selection, statistical characterization, control-limit establishment, quantitative objective setting, subprocess monitoring, and statistical management.*

This skill implements quantitative process management by computing process
performance baselines, setting statistical control limits, generating SPC
control charts, detecting out-of-control processes, and producing QPM reports
with improvement recommendations. It enables CMMI Level 4 execution by turning
historical KPI data into statistically grounded management limits and
project-level action signals.

### Scope

| In Scope | Out of Scope |
|---|---|
| Baseline computation: mean (μ) and standard deviation (σ) | Raw metric collection — delegated to `cmmi-metrics-collection` |
| Control limits: UCL = μ + 3σ; LCL = max(0, μ - 3σ) | Root cause analysis — delegated to Level 5 CAR practices |
| SPC control chart generation in Markdown tables and ASCII art | Process change implementation |
| Out-of-control detection using Western Electric rules | Manual data cleansing outside the provided metrics stores |
| QPM reporting and quantitative objective setting | KPI definition changes without governance approval |

### Audience

- Metrics Analysts maintaining organizational and project KPI baselines.
- EPG Leads governing Level 4 quantitative management adoption.
- SQA Auditors reviewing statistical control evidence and QPM findings.
- Project Managers consuming quantitative objectives and trend reports.

### References & Definitions

| Term | Definition |
|---|---|
| Process Performance Baseline (PPB) | Quantitative characterization of a process's expected performance, derived from historical data |
| Statistical Process Control (SPC) | Using statistical methods to monitor and control a process |
| Control Chart | Graph showing process data over time with control limits (UCL, center line, LCL) |
| Out-of-Control | Process data outside control limits or exhibiting non-random patterns |
| Western Electric Rules | Standard rules for detecting out-of-control signals: 1 point beyond 3σ, 2 of 3 beyond 2σ, 4 of 5 beyond 1σ, or 8 consecutive points on one side of the center line |
| Quantitative Objective | A target derived from baseline statistics, such as μ - 1σ for a lower-bound performance goal |

### References

| Reference | Location |
|---|---|
| Organizational baselines | `projects/<project>/docs/metrics/org-baselines.json` |
| Project metrics store | `projects/<project>/docs/metrics/metrics-store.json` |
| Governance workflows | `config/skills/cmmi-glue/SKILL.md` |
| Framework coherency audit consumer | `config/skills/cmmi-coherency-audit/SKILL.md` |

### Referenced Skills

| Skill | Role in Workflow |
|---|---|
| `cmmi-metrics-collection` | Upstream provider of normalized KPI time-series input data |
| `cmmi-glue` | Governance workflow authority; Workflow 1 controls tailoring and Workflow 4 consumes QPM trends |
| `cmmi-coherency-audit` | Downstream consumer that uses QPM health and control evidence as audit input |

---

## 3. RACI Matrix

*Practice areas: QPM SP 1.3 and QPM SP 1.4 — every quantitative management activity has explicit responsibility and accountability.*

| Task | Activity | Metrics Analyst | EPG Lead | SQA Auditor | Configuration Manager |
|---|---|---|---|---|---|
| T1 | Load organizational baselines and project metrics | R | A | C | I |
| T2 | Compute process performance baselines (μ, σ) | R | A | C | I |
| T3 | Set control limits (UCL, LCL) | R | A | C | I |
| T4 | Generate SPC control charts | R | A | C | I |
| T5 | Apply Western Electric rules | R | A | C | I |
| T6 | Record out-of-control findings | R | A | C | I |
| T7 | Set quantitative objectives from baselines | R | A | C | I |
| T8 | Produce and file QPM report | R | A | C | I |

---

## 4. Process Architecture (Extended ETVX Model)

*Practice areas: OPP SP 1.2, OPP SP 1.3, QPM SP 1.1, and QPM SP 1.4 — defines the quantitative management workflow, statistical controls, and project-level decision outputs.*

### E — Entry Criteria

All conditions must evaluate to true before starting quantitative analysis:

- [ ] Organizational baselines exist at `projects/<project>/docs/metrics/org-baselines.json` with at least 3 data points per KPI, provided by `cmmi-metrics-collection`.
- [ ] A per-project metrics store exists at `projects/<project>/docs/metrics/metrics-store.json`.

### I — Inputs & Sources

| Input | Source | Format |
|---|---|---|
| Organizational KPI history | `projects/<project>/docs/metrics/org-baselines.json` | JSON time-series by KPI |
| Project KPI history | `projects/<project>/docs/metrics/metrics-store.json` | JSON time-series by KPI and run |
| Project identifier | User input or project directory name | Text |
| Previous QPM report | `projects/<project>/docs/reports/` | Markdown |

### T — Tasks / Activities

1. **Load baseline sources.** Load organizational baselines from `projects/<project>/docs/metrics/org-baselines.json` and per-project metrics from `projects/<project>/docs/metrics/metrics-store.json`.
2. **Compute Process Performance Baselines.** For each KPI with at least 3 data points, compute mean (μ) and standard deviation (σ).
3. **Set control limits.** For each eligible KPI, compute UCL = μ + 3σ and LCL = max(0, μ - 3σ).
4. **Generate SPC control charts.** Create one Markdown section per KPI with a summary table and an ASCII-art control chart. Example:

```text
KPI: audit_pass_rate (%)
UCL ─── 100.0 ──────────────────────────
         │     *   *       *
μ   ─── 96.7 ──*───*───────────*────────
         │  *
LCL ─── 85.0 ──────────────────────────
        run1  run2 run3 run4 run5 run6
```

5. **Apply Western Electric rules.** Detect out-of-control signals using these rules:
    - Rule 1: 1 point beyond 3σ.
    - Rule 2: 2 of 3 consecutive points beyond 2σ on the same side of μ.
    - Rule 3: 4 of 5 consecutive points beyond 1σ on the same side of μ.
    - Rule 4: 8 consecutive points on the same side of μ.
6. **Produce findings.** For each out-of-control signal, record KPI name, current value, baseline, deviation, and recommended investigation.
7. **Set quantitative objectives.** Replace qualitative targets such as `≥90%` with statistically grounded objectives such as `μ - 1σ = 92.3%`.
8. **Produce the QPM report.** File `projects/<project>/docs/reports/qpm-report-<NNN>.md` with KPI summaries, SPC charts, out-of-control findings, updated quantitative objectives, and improvement recommendations.

#### Writing Constraints

| Rule | Requirement |
|---|---|
| Binary verdicts | Every quantitative control check produces PASS or FAIL with evidence. No "partially compliant." |
| No Conversational Prose | Use imperative, professional technical writing. Banned terms: "periodic," "as needed," "appropriate," "generally," "when ready." Use precise statistical thresholds and absolute conditions. |
| Statistical precision | Express baselines, control limits, deviations, and quantitative objectives numerically. Do not replace computed values with qualitative summaries. |
| Practice-Area Citation | Cite OPP SP 1.1, OPP SP 1.2, OPP SP 1.3, QPM SP 1.1, QPM SP 1.2, QPM SP 1.3, or QPM SP 1.4 by ID in each major section of the output. |

### V — Verification & Validation

*Practice areas: OPP SP 1.3 and QPM SP 1.4 — objective evaluation of statistical validity and project-control outputs.*

Before delivering the output, verify all of the following:

- [ ] Every task in §4.T maps to at least one Responsible role and one Accountable role in §3.
- [ ] Every KPI with at least 3 data points has recorded μ, σ, UCL, and LCL values.
- [ ] Every generated SPC chart includes UCL, center line (μ), LCL, and run labels.
- [ ] Western Electric rules were applied to every KPI that has control limits.
- [ ] Every out-of-control finding includes KPI name, current value, baseline, deviation, and recommended investigation.
- [ ] Every quantitative objective in the QPM report is expressed as a statistical target derived from the latest baseline.
- [ ] Control limits (UCL/LCL) are documented in the QPM report for each KPI with sufficient data.
- [ ] The QPM report cites OPP SP 1.1, OPP SP 1.2, OPP SP 1.3, QPM SP 1.1, QPM SP 1.2, QPM SP 1.3, and QPM SP 1.4 by ID.

### X — Exit Criteria

- [ ] SPC control charts are generated for all KPIs with sufficient data.
- [ ] Out-of-control signals are classified and documented.
- [ ] The QPM report is filed.
- [ ] Quantitative objectives are updated based on the latest baselines.
- [ ] Non-conformances found during verification are escalated per `cmmi-glue` Workflow 3 (SQA Audit & Non-Compliance Escalation).

### O — Outputs & Destinations

| Output | Format | Destination |
|---|---|---|
| QPM report | Markdown | `projects/<project>/docs/reports/qpm-report-<NNN>.md` |
| SPC charts embedded in QPM report | Markdown tables and ASCII art | Embedded in `projects/<project>/docs/reports/qpm-report-<NNN>.md` |

---

## 5. Measurement and Metrics

*Practice areas: OPP SP 1.2, OPP SP 1.3, QPM SP 1.1, and QPM SP 1.4 — monitor baseline quality, statistical stability, and objective attainment.*

| KPI | Formula | Collection Point | Organisational Objective |
|---|---|---|---|
| Baseline stability | (KPIs where σ decreased vs previous quarter) / (total managed KPIs) × 100 | `projects/<project>/docs/reports/qpm-report-<NNN>.md` | Increase process stability quarter over quarter across managed KPIs |
| Out-of-control rate | (KPIs with active out-of-control signals) / (total active KPIs) × 100 | `projects/<project>/docs/reports/qpm-report-<NNN>.md` | Keep unstable KPIs below 10% of the active KPI set |
| Prediction accuracy | (projects whose KPIs fell within control limits) / (total in-scope projects) × 100 | `projects/<project>/docs/reports/qpm-report-<NNN>.md` | Keep at least 90% of in-scope project KPI results inside statistical limits |
| Quantitative objective hit rate | (quantitative objectives met) / (total quantitative objectives) × 100 | `projects/<project>/docs/reports/qpm-report-<NNN>.md` | Achieve at least 85% attainment of statistically derived objectives |

### Metric Collection Path

All QPM metrics are collected in the project report at:
`projects/<project>/docs/reports/qpm-report-<NNN>.md`

The Metrics Analyst reads baseline data from
`projects/<project>/docs/metrics/org-baselines.json` (owned by `cmmi-metrics-collection`).
QPM analysis results and control limits are documented in the QPM report.
Aggregated trends feed into `cmmi-glue` Workflow 4 for organization-level
improvement decisions.

### Governance Review Cadence

The EPG Lead reviews each QPM report within 5 working days of report filing.
The organizational baseline set is reviewed quarterly for baseline resets,
control-limit drift, and quantitative objective revisions.

---

## 6. Tailoring Guidelines

*Practice areas: OPD SP 1.1, QPM SP 1.1, and QPM SP 1.4 — controlled tailoring of Level 4 statistical management. All deviations follow `cmmi-glue` Workflow 1.*

| Deviation | Conditions for Approval | Approval Authority |
|---|---|---|
| Defer QPM for Profile S or M | Fewer than 5 completed project runs exist for the KPI set | EPG Lead |
| Run Profile S or M in assessment-only mode | At least 3 completed runs exist; generate baselines and charts, but do not reset quantitative objectives | EPG Lead |
| Require full QPM for Profile L | At least 3 completed project runs exist | No deviation — full QPM execution required |
| Skip the skill entirely | 2 or fewer completed project runs exist | Entry criteria not met; record the skip in the governance record |
| **Profile-P (PyCSL): Phase 0 snapshot accumulation** | Defer QPM control-chart generation until `bin/cmmi-metrics-ingest.py --weekly` has appended ≥8 weekly snapshots to `projects/pycsl/docs/metrics/metrics-store.json`. Phase 0 records per-system KPIs only — no control limits, no objectives, no out-of-control signals — until enough data exists. PyCSL-priority charts (added at Phase 1): (a) proof-success rate per system per week, (b) agent retry-count drift, (c) L3-ceiling rate trend per system, (d) doc-coherency events per week. | Developer (single-developer CCB) |

### Approval Authority

The EPG Lead approves tailoring requests with SQA Auditor concurrence before
execution. Record each approved deviation in the QPM report under a
"Tailoring Deviations" section and route the record through `cmmi-glue`
Workflow 1.

---

*This document is a Configuration Item (CI) under baseline BL-QPM-001.
Changes require Change Control Board approval per `cmmi-glue` Workflow 2.*
