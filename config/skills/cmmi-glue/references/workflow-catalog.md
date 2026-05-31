# Workflow Catalog — Cross-Role Governance Workflows

This reference defines the four cross-role governance workflows that connect
organizational roles to each other. These workflows are company-wide processes
triggered at different stages of the project lifecycle. They are not
project-specific — every project must implement them (subject to tailoring).

## How to Use This File

1. For each workflow, check the **Trigger Condition** to determine when it activates.
2. Follow the **Role Interaction Sequence** step by step.
3. At each **Decision Gate**, determine the outcome before proceeding.
4. Record the **Output Artifacts** in the project's CM repository.

---

## Workflow 1 — Tailoring Process

*From organizational standard to project-specific plan.*

### Summary

| Field | Value |
|---|---|
| Purpose | Adapt the standard 5-level specification framework to a specific project's size, risk, and complexity |
| Who Starts | Project Manager |
| Who Governs | EPG/SEPG + SQA Auditor |
| Output | A right-sized Project Management Plan (PMP) with approved tailoring deviations |
| CMMI Practice Area | OPD (Organizational Process Definition) |

### Trigger Condition

- [ ] A new project is initiated and the standard 5-level framework must be adapted.
- [ ] An existing project's scope changes significantly (requiring re-tailoring).

### Role Interaction Sequence

```
Step  Role                   Action
────  ─────────────────────  ──────────────────────────────────────────────────
1     Project Manager        Reviews project size, risk, and complexity.
2     Project Manager        Applies Tailoring Guidelines (defined by EPG) to
                             determine which documentation levels, V-cycle
                             steps, or artifacts can be skipped or condensed.
3     Project Manager        Submits a Tailoring Request to the EPG.
 ── DECISION GATE 1 ──────────────────────────────────────────────────────────
4     EPG/SEPG               Reviews the Tailoring Request against
                             organizational standards.
5     SQA Auditor            Independently verifies that the proposed
                             tailoring does not violate CMMI compliance
                             requirements.
 ── DECISION GATE 2 ──────────────────────────────────────────────────────────
6a    EPG + SQA              APPROVE → The tailored plan becomes the
                             project's official baseline.
6b    EPG + SQA              REJECT → Return to Step 2 with feedback.
                             The PM must revise the Tailoring Request.
────  ─────────────────────  ──────────────────────────────────────────────────
7     Configuration Manager  Baselines the approved tailored PMP in the
                             CM repository.
```

### Decision Gates

| Gate | Question | Approve Condition | Reject Condition |
|---|---|---|---|
| Gate 1 | Does the tailoring comply with organizational standards? | All proposed deviations are within the EPG's allowed deviation catalog | A proposed deviation violates a mandatory process requirement |
| Gate 2 | Does the tailoring maintain CMMI compliance? | SQA confirms no CMMI practice area is left unaddressed | SQA identifies a practice area that would be unaddressed after tailoring |

### Output Artifacts

| Artifact | Owner | Destination |
|---|---|---|
| Tailoring Request | Project Manager | CM repository |
| Tailoring Approval Record | EPG + SQA | CM repository |
| Tailored Project Management Plan (PMP) | Project Manager | CM repository, baselined |

### Pre-Approved Profile Fast-Track

When a Project Manager selects a pre-approved tailoring profile (S or M), the
standard tailoring ceremony is abbreviated:

| Step | Action |
|------|--------|
| 1 | PM evaluates project against profile selection criteria (`project-lifecycle/references/tailoring-profiles.md`) |
| 2 | PM declares the selected profile in `PROJECT.md` |
| 3 | PM creates a Tailoring Request citing the pre-approved profile |
| 4 | Tailoring Request is **auto-approved** — Gates 1 and 2 are waived |
| 5 | Configuration Manager baselines the PMP |

**Conditions for fast-track:**
- The project must meet **all** criteria for the selected profile
- If any criterion falls outside the profile's range, the full ceremony applies
- Profile L always requires the full ceremony (Steps 1–7 above)

**Escalation:** If a project outgrows its profile during execution, a Change
Request (Workflow 2) must be raised to escalate to a heavier profile.

---

## Workflow 2 — Change Control

*Cross-role integrity when requirements change.*

### Summary

| Field | Value |
|---|---|
| Purpose | Govern how a requirement change at any level cascades across all 5 specification levels without documentation/code drift |
| Who Starts | Business Analyst / Client |
| Who Governs | Configuration Manager + Change Control Board (CCB) |
| Output | A newly approved, synchronized baseline across all affected levels |
| CMMI Practice Areas | CM (Configuration Management), RDM (Requirements Development and Management) |

### Trigger Condition

- [ ] A change request is received from a stakeholder, client, or internal team.
- [ ] A defect or gap discovered during verification requires a specification change.

### Role Interaction Sequence

```
Step  Role                   Action
────  ─────────────────────  ──────────────────────────────────────────────────
1     Business Analyst       Receives or initiates a Change Request (CR).
2     Business Analyst       Performs an impact analysis: identifies which
                             specification levels (1–5) are affected by
                             the change.
3     Configuration Manager  Registers the CR in the change tracking system.
4     Configuration Manager  Schedules a Change Control Board (CCB) meeting.
 ── DECISION GATE 1 ──────────────────────────────────────────────────────────
5     CCB (PM, System        Reviews the CR, impact analysis, and
      Architect, QA Lead)    budget/timeline implications. Votes to
                             approve, reject, or defer the change.
 ── DECISION GATE 2 ──────────────────────────────────────────────────────────
5a    CCB                    APPROVE → Proceed to Step 6.
5b    CCB                    REJECT → CR is closed with rationale recorded.
5c    CCB                    DEFER → CR is placed in backlog with priority.
────  ─────────────────────  ──────────────────────────────────────────────────
6     Configuration Manager  Unlocks the affected repository baselines at
                             each impacted specification level.
6a    Business Analyst       Updates Level 1 specifications (BRD, use
                             cases, business requirements) if affected.
7     System Architect       Updates Level 2 specifications (SRS, SAD, ICD)
                             if affected.
8     Technical Lead         Updates Level 3 specifications (HLD, component
                             interfaces, APIs) if affected.
9     Software Engineer      Updates Level 4 specifications (MLD, module
                             design) if affected.
9a    Software Engineer      Updates Level 5 artifacts (LLD, unit
                             annotations, code) if affected.
10    Test Engineers          Update test plans and test cases at each
                             affected level.
11    Configuration Manager  Re-audits all updated artifacts for
                             consistency across levels.
 ── DECISION GATE 3 ──────────────────────────────────────────────────────────
12a   Configuration Manager  All artifacts consistent → Locks the new
                             baseline. CR is closed as resolved.
12b   Configuration Manager  Inconsistencies found → Return to Step 7
                             with discrepancy report.
```

### Decision Gates

| Gate | Question | Approve Condition | Reject Condition |
|---|---|---|---|
| Gate 1 | Should the change be implemented? | Business value justifies cost/schedule impact; no unacceptable risk | Cost/schedule impact exceeds threshold; unacceptable risk |
| Gate 2 | Are all affected levels updated consistently? | CM audit confirms all specifications, code, and tests are synchronized | CM audit finds drift between specification levels |

### Cascade Impact Matrix

| Change Origin Level | Levels Potentially Affected | Roles Involved in Update |
|---|---|---|
| Level 1 (Business) | Levels 1, 2, 3, 4, 5 | BA, System Architect, Tech Lead, Developer, all Test Engineers |
| Level 2 (System) | Levels 3, 4, 5 | System Architect, Tech Lead, Developer, Integration/Module/Unit Test Engineers |
| Level 3 (Component) | Levels 4, 5 | Tech Lead, Software Engineer, Module/Unit Test Engineer |
| Level 4 (Module) | Level 5 | Software Engineer, Unit Test Engineer |
| Level 5 (Unit) | None (isolated) | Software Engineer, Unit Test Engineer |

### Output Artifacts

| Artifact | Owner | Destination |
|---|---|---|
| Change Request (CR) | Business Analyst | Change tracking system |
| Impact Analysis | Business Analyst | Attached to CR |
| CCB Decision Record | Configuration Manager | CM repository |
| Updated specifications (per affected level) | Respective Specifiers | CM repository, re-baselined |
| Updated test plans/cases | Test Engineers | CM repository |
| Baseline Audit Report | Configuration Manager | CM repository |

---

## Workflow 3 — SQA Audit & Non-Compliance Escalation

*Process compliance verification with teeth.*

### Summary

| Field | Value |
|---|---|
| Purpose | Verify that engineering roles follow defined processes; handle non-compliance with corrective action and escalation |
| Who Starts | SQA Auditor |
| Who Governs | Upper Management / EPG (if escalated) |
| Output | Non-Compliance Reports (NCRs) and verified corrective actions |
| CMMI Practice Area | PQA (Process Quality Assurance) |

### Trigger Condition

- [ ] A scheduled project checkpoint is reached (e.g., design review, code review gate, test completion milestone).
- [ ] An ad-hoc audit is initiated based on risk indicators or management request.

### Role Interaction Sequence

```
Step  Role                   Action
────  ─────────────────────  ──────────────────────────────────────────────────
1     SQA Auditor            Reviews a project checkpoint against the
                             defined process (e.g., "Was the HLD
                             peer-reviewed before lower-level specification began?").
 ── DECISION GATE 1 ──────────────────────────────────────────────────────────
2a    SQA Auditor            COMPLIANT → Records positive finding.
                             No further action required.
2b    SQA Auditor            NON-COMPLIANT → Proceeds to Step 3.
────  ─────────────────────  ──────────────────────────────────────────────────
3     SQA Auditor            Issues a Non-Compliance Report (NCR) to the
                             responsible Engineering role (e.g., Tech Lead).
4     Engineering Role       Acknowledges the NCR within the defined
      (e.g., Tech Lead)      response timeframe (e.g., 5 business days).
5     Engineering Role       Provides a Corrective Action Plan (CAP) with
                             specific remediation steps and deadline.
 ── DECISION GATE 2 ──────────────────────────────────────────────────────────
6a    SQA Auditor            CAP is adequate → Monitors execution.
6b    SQA Auditor            CAP is inadequate or not provided within
                             timeframe → Proceeds to Step 7 (escalation).
────  ─────────────────────  ──────────────────────────────────────────────────
7     SQA Auditor            Escalates to Upper Management or EPG with
                             the NCR and evidence of non-response.
8     Upper Management       Directs the Engineering role to comply or
      / EPG                  authorizes a process exception (documented).
────  ─────────────────────  ──────────────────────────────────────────────────
9     SQA Auditor            Verifies that the corrective action has been
                             executed. Closes the NCR.
```

### Decision Gates

| Gate | Question | Pass Condition | Fail Condition |
|---|---|---|---|
| Gate 1 | Was the defined process followed? | All required artifacts exist and were produced in the correct sequence | A required artifact is missing, or process steps were skipped |
| Gate 2 | Is the corrective action adequate? | CAP addresses root cause with specific steps and deadline; provided within response timeframe | CAP is vague, does not address root cause, or was not provided within the response timeframe |

### Escalation Path

```
SQA Auditor → Engineering Role (NCR)
    ↓ (if unresolved within response timeframe)
SQA Auditor → Upper Management / EPG (escalation)
    ↓ (management directive)
Engineering Role → Corrective Action
    ↓ (verification)
SQA Auditor → NCR Closure
```

### Output Artifacts

| Artifact | Owner | Destination |
|---|---|---|
| Audit Checklist / Findings | SQA Auditor | CM repository |
| Non-Compliance Report (NCR) | SQA Auditor | CM repository, sent to responsible role |
| Corrective Action Plan (CAP) | Engineering Role | CM repository, attached to NCR |
| Escalation Record | SQA Auditor | CM repository, sent to management |
| NCR Closure Record | SQA Auditor | CM repository |

---

## Workflow 4 — Continuous Improvement Loop

*The metrics engine that evolves processes over time.*

### Summary

| Field | Value |
|---|---|
| Purpose | Collect process data, identify trends, and update organizational standards based on evidence — this differentiates CMMI Level 2 from Level 3+ |
| Who Starts | Developers + Test Engineers (data logging) |
| Who Governs | EPG/SEPG |
| Output | Updated, optimized organizational standards and process assets |
| CMMI Practice Areas | MPM (Managing Performance and Measurement), OPD (Organizational Process Definition), OPP (Organizational Process Performance), QPM (Quantitative Project Management) |

### Trigger Condition

- [ ] A governance review cycle is reached (minimum: once per quarter).
- [ ] A significant trend is detected in collected metrics (threshold breach).

### Role Interaction Sequence

```
Step  Role                   Action
────  ─────────────────────  ──────────────────────────────────────────────────
1     Software Engineers     Log process data during the V-cycle (e.g.,
      + Test Engineers       time spent on peer reviews, defect counts by
                             level, test coverage percentages).
2     Metrics Analyst        Extracts data from project repositories,
                             test tools, and CI/CD pipelines.
                             Invokes `cmmi-metrics-collection` to aggregate
                             §5 KPIs into the metrics store.
3     Metrics Analyst        Analyzes trends and identifies correlations
                             (e.g., "Projects spending < 2 hours on HLD
                             peer reviews see a 40% spike in unit-test
                             bugs").
3a    Metrics Analyst        Computes/updates process performance baselines
                             (mean, σ) per KPI using `cmmi-metrics-collection`.
                             Flags KPIs with <3 data points as insufficient.
4     Metrics Analyst        Produces a Process Performance Report and
                             presents findings to the EPG.
4a    Metrics Analyst        Generates SPC control charts and detects
                             out-of-control signals using
                             `cmmi-quantitative-mgmt`. Flags KPIs outside
                             UCL/LCL or violating Western Electric rules.
 ── DECISION GATE 1 ──────────────────────────────────────────────────────────
5a    EPG/SEPG               Findings are actionable → Proceeds to Step 6.
5b    EPG/SEPG               Findings are inconclusive → Requests
                             additional data collection. Return to Step 2.
────  ─────────────────────  ──────────────────────────────────────────────────
6     EPG/SEPG               Updates the standard process documentation,
                             templates, or tailoring guidelines based on
                             the evidence.
7     EPG/SEPG               Updates the Process Asset Library (PAL) with
                             the revised standards.
8     Configuration Manager  Baselines the updated process assets in the
                             CM repository.
9     SQA Auditor            Adds the new/updated process requirements
                             to future audit checklists.
────  ─────────────────────  ──────────────────────────────────────────────────
      (Loop restarts at Step 1 with updated standards in effect.)
```

### Decision Gates

| Gate | Question | Proceed Condition | Recycle Condition |
|---|---|---|---|
| Gate 1 | Are the findings actionable? | Data shows a statistically significant trend with a clear process improvement recommendation | Data is insufficient, contradictory, or the sample size is too small to draw conclusions |

### Output Artifacts

| Artifact | Owner | Destination |
|---|---|---|
| Process data logs | Engineers + Testers | Metrics database / CI/CD pipeline |
| Process Performance Report | Metrics Analyst | Presented to EPG |
| Updated standard processes / templates | EPG/SEPG | Process Asset Library (PAL) |
| Updated tailoring guidelines | EPG/SEPG | PAL |
| Revised audit checklists | SQA Auditor | PAL |

### Skill Metric Sources

Workflow 4 consumes metrics from all CMMI skills. The Metrics Analyst
collects data from these skill-specific collection paths:

| Skill | Metric Collection Path |
|---|---|
| `cmmi-agent-roles` | `projects/<project>/docs/reports/role-assignment-report.md` |
| `cmmi-documents` | Each document's §1 revision history + `projects/<project>/docs/reports/` |
| `cmmi-process-level` | `projects/<project>/docs/reports/gap-<topic>-<NNN>.md` |
| `cmmi-glue` | `projects/<project>/docs/process/` (governance artifacts) + `projects/<project>/docs/audits/` (NCR data) |
| `communication` | `projects/<project>/message-queues/` (message files + agent logs) |
| `cmmi-coherency-audit` | `projects/<project>/docs/audits/coherency-audit-<NNN>.md` |
| `project-lifecycle` | `projects/<project>/docs/reports/metrics-collection-<NNN>.md`, `projects/<project>/docs/reports/` (reconciliation logs) |
| `import-existing-code` | `projects/<project>/docs/reports/metrics-collection-<NNN>.md` (via `cmmi-metrics-collection`), `projects/<project>/docs/reports/sqa-import-summary.md` |
| `cmmi-metrics-collection` | `projects/<project>/docs/metrics/metrics-store.json` + `projects/<project>/docs/reports/metrics-collection-<NNN>.md` |
| `cmmi-quantitative-mgmt` | `projects/<project>/docs/reports/qpm-report-<NNN>.md` + `projects/<project>/docs/metrics/org-baselines.json` |
| `spin-modeling` | `projects/<project>/docs/reports/` (verification evidence, per-run metrics) |

---

## Cross-Workflow Summary

| Workflow | Who Starts | Who Governs | Output | CMMI Level Requirement |
|---|---|---|---|---|
| Tailoring | Project Manager | EPG + SQA | Right-sized Project Management Plan | Level 2+ |
| Change Control | Business Analyst / Client | CM + CCB | Newly approved, synchronized baseline | Level 2+ |
| SQA Audit & Escalation | SQA Auditor | Upper Management (if escalated) | NCRs + verified corrective actions | Level 2+ |
| Continuous Improvement | Developers + Testers (data) / Metrics Analyst (analysis) | EPG | Updated organizational standards | Level 3+ (mandatory) |
