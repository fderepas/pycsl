---
name: cmmi-coherency-audit
description: >
  Runs a complete framework-wide coherency audit across all skills in
  config/skills/. Combines four lens-based intra-skill audits (polish-skill,
  cmmi-documents, cmmi-agent-roles, cmmi-glue), structural audits (ETVX ×
  V-Model compatibility), and seven cross-skill coherency checks (reference
  integrity, term consistency, entry→exit chain, output path agreement, ID
  uniqueness, README drift, metric framework coherency). Produces a single
  unified report. Use when the user asks to audit the full framework, run a
  coherency check, verify cross-skill consistency, validate the skill library,
  or perform a comprehensive quality audit of all skills.
document_id: SKILL-CMMI-COHER-001
version: "1.0"
status: Approved
effective_date: "2026-05-22"
baseline_id: BL-COHER-001
cmmi_version: "2.0"
practice_areas:
  - "PQA SP 1.1 — Objectively Evaluate Processes"
  - "OPD SP 1.1 — Establish Standard Processes"
  - "CM SP 1.1 — Establish Baselines"
---

# CMMI Framework Coherency Audit

## 1. Document Control & Metadata

| Field | Value |
|---|---|
| Document ID | SKILL-CMMI-COHER-001 |
| Version | 1.0 |
| Status | Approved |
| Effective Date | 2026-05-22 |
| Baseline ID | BL-COHER-001 |
| CMMI Version | 2.0 |

### Revision History

| Version | Date | Author | Change Summary |
|---|---|---|---|
| 1.0 | 2026-05-22 | Agent (EPG) | Initial release — unified audit combining 4 lens audits + 7 cross-skill checks |

### Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| Accountable — EPG Lead | _(pending)_ | | |
| Responsible — SQA Auditor | _(pending)_ | | |

---

## 2. Introduction & Context

### Purpose

*Practice area: PQA SP 1.1 — objective evaluation of organizational process
assets for internal consistency and completeness.*

This skill runs a **complete framework-wide coherency audit** across all
skills in `config/skills/`. It replaces the need to manually invoke
individual audit commands by combining:

1. **Four lens-based intra-skill audits** — each CMMI skill becomes an
   audit lens applied to all other skills.
2. **Structural audits** — ETVX × V-Model compatibility checks for skills
   with internal process structures.
3. **Seven cross-skill coherency checks** — verifying the interfaces,
   references, and contracts *between* skills.
4. **README accuracy verification** — ensuring the top-level documentation
   matches the current framework state.

### Scope

| In Scope | Out of Scope |
|---|---|
| All skills in `config/skills/` | Project-instance artifacts under `projects/` |
| All personas in `config/agents/` | Source code in `src/` |
| `README.md` accuracy | External documentation or third-party tools |
| Cross-skill reference integrity | Individual project lifecycle execution |
| Metric framework coherency | Running actual tests or builds |

### Audience

- SQA Auditors running the framework-wide audit.
- EPG Members maintaining the skill library.
- Any agent validating framework integrity after a change.

> **Downstream re-validation:** When a skill is updated to a new version
> (e.g., import-existing-code v1.0 → v2.0), projects that were produced
> under the previous version should be re-validated against the new
> version's requirements. This is distinct from the framework-level audit
> and is performed per-project using the updated skill's compliance checks.

### References & Definitions

| Term | Definition |
|---|---|
| Lens audit | Applying one skill's criteria as an audit checklist against all other skills |
| Cross-skill coherency | Consistency of references, terms, paths, and contracts between skills |
| Entry→exit chain | The property that skill A's exit criteria guarantee skill B's entry criteria when A's output feeds into B |
| README drift | Divergence between the README's claims and the actual framework state |

### References

| Reference | Location |
|---|---|
| Polish-skill checklist | `config/skills/polish-skill/SKILL.md` |
| CMMI-documents V&V | `config/skills/cmmi-documents/SKILL.md` §4.V |
| Agent-roles criteria | `config/skills/cmmi-agent-roles/SKILL.md` |
| Governance workflows | `config/skills/cmmi-glue/SKILL.md` |
| V-Model lifecycle | `config/skills/project-lifecycle/SKILL.md` |
| Cross-skill checklist | `references/cross-skill-checklist.md` |

### Referenced Skills

| Skill | Role in Audit |
|---|---|
| `polish-skill` | Lens A1 — writing quality (17-point checklist) |
| `cmmi-documents` | Lens A2 — §1–§6 compliance (9-point V&V) |
| `cmmi-agent-roles` | Lens A3 — persona/RACI/coverage validation |
| `cmmi-glue` | Lens A4 — governance workflow compliance |
| `project-lifecycle` | Structural audit target (ETVX × V-Model) |
| `cmmi-process-level` | Cross-ref target for level definitions |
| `cmmi-metrics-collection` | Metric infrastructure audit target |
| `cmmi-quantitative-mgmt` | QPM/OPP audit target |

---

## 3. RACI Matrix

*Practice area: PQA SP 1.1 — role-to-task mapping for the coherency audit.*

| Task | Activity | SQA Auditor | EPG Lead | EPG Member | All stakeholders¹ |
|---|---|---|---|---|---|
| A1 | Polish-skill lens audit | R | A | — | I |
| A2 | CMMI-documents lens audit | R | A | — | I |
| A3 | Agent-roles lens audit | R | A | — | I |
| A4 | CMMI-glue lens audit | R | A | — | I |
| B1 | ETVX × V-Model structural audit | R | A | — | — |
| B2 | ETVX completeness structural audit | R | A | — | — |
| C1–C7 | Cross-skill coherency checks | R | A | C | — |
| D1 | Aggregate findings | R | A | — | — |
| D2 | Produce unified report | R | A | — | I |
| D3 | Fix actionable findings | C | A | R | — |

¹ Broadcast notification pattern — not a single persona.

---

## 4. Process Architecture (Extended ETVX Model)

*Practice areas: PQA SP 1.1 — defines the comprehensive audit process;
OPD SP 1.1 — evaluates organizational process assets.*

### E — Entry Criteria

All conditions must evaluate to true before starting the audit:

- [ ] The skill library at `config/skills/` contains at least one skill.
- [ ] Agent personas exist in `config/agents/`.
- [ ] `README.md` exists at repository root.
- [ ] The auditor has read access to all skills, personas, and the README.

### I — Inputs & Sources

| Input | Source | Format |
|---|---|---|
| All SKILL.md files | `config/skills/*/SKILL.md` | Markdown with YAML frontmatter |
| All reference files | `config/skills/*/references/*.md` | Markdown |
| All persona files | `config/agents/*.md` | Markdown with YAML frontmatter |
| README | `README.md` | Markdown |
| Cross-skill checklist | `references/cross-skill-checklist.md` | Markdown checklist |
| Project name | User input | Text (for report output path) |

### T — Tasks / Activities

The audit executes in four phases. Each phase produces findings classified as
Critical, Major, Minor, or Observation.

#### Phase A — Lens-Based Intra-Skill Audits

For each skill S in `config/skills/`:

**A1. Polish-skill lens.** Apply the 17-point failure-mode checklist from
`config/skills/polish-skill/SKILL.md`:
1. Verify YAML frontmatter completeness.
2. Check for banned terms ("periodic," "as needed," "appropriate," "generally," "when ready").
3. Verify all code fences have language tags.
4. Check trigger specificity (description covers all intended use cases).
5. Verify no forward references to undefined skills or files.
6. Check file size (<500 lines for main SKILL.md).
7. Run all 17 checks; record pass/fail per skill.

**A2. CMMI-documents lens.** Apply the 9-point V&V checklist and §1–§6
structure check from `config/skills/cmmi-documents/SKILL.md`:
1. Verify §1 Document Control (revision history, approvals, baseline ID).
2. Verify §2 Introduction (purpose with practice-area citations by SP ID, scope, audience, references).
3. Verify §3 RACI (every task has R + A; covers all ETVX tasks).
4. Verify §4 ETVX (all 6 components: E, I, T, V, X, O; binary entry/exit criteria).
5. Verify §5 Metrics (KPIs with collection path, tied to organizational objectives).
6. Verify §6 Tailoring (deviations, conditions, approval authority for L3+).
7. Verify writing constraints (no banned terms, practice areas cited by SP ID).
8. Verify CI marking with baseline ID.
9. Record pass/fail per skill. Non-CMMI skills (agent-project-structure, polish-skill, plantuml, system-design-paradigms) are audited on writing constraints only; §1–§6 structural checks are N/A.

**A3. Agent-roles lens.** Apply persona compliance, RACI naming, persona↔skill
mapping, and coverage validation from `config/skills/cmmi-agent-roles/SKILL.md`:
1. Verify all persona files in `config/agents/` against the persona template (required YAML fields + markdown sections).
2. Verify all RACI column headers use role-catalog names (not generic terms).
3. Cross-check: every skill listed in a persona's `skills:` array exists in `config/skills/`.
4. Cross-check: every skill's RACI roles have corresponding persona files.
5. Verify spec-level coverage rule: each level has Specifier + Governance + Verifier.
6. Record pass/fail per dimension.

**A4. CMMI-glue lens.** Apply governance workflow compliance from
`config/skills/cmmi-glue/SKILL.md`:
1. Verify each CMMI skill references at least one of the 4 governance workflows (Tailoring, Change Control, SQA Audit & Non-Compliance Escalation, Continuous Improvement) where applicable.
2. Verify each baselined `SKILL.md` ends with an explicit CI declaration. Do not treat §4.O project-level outputs as missing CI declarations; those outputs are managed as project CIs.
3. Verify skills with tailoring sections reference the Tailoring workflow from cmmi-glue.
4. Verify the change control cascade covers all spec levels defined across skills.
5. Record pass/fail per skill.

#### Phase B — Structural Audits

**B1. ETVX × V-Model compatibility** (for `project-lifecycle` only):
1. Verify the §4 ETVX Tasks map cleanly to recursive level-based execution (T2–T6).
2. Verify per-phase entry/exit criteria in the reference file are consistent with the ETVX.
3. Verify nested loop markers are consistent (all phases within a loop have iteration markers).
4. Verify the V-diagram and dependency graph are internally consistent.
5. Record pass/fail per check.

**B2. ETVX completeness** (for all CMMI skills):
1. Verify §4 has all 6 ETVX components (E, I, T, V, X, O).
2. Verify entry criteria are binary (checkboxes, not prose).
3. Verify exit criteria are binary.
4. Verify every ETVX task appears in the RACI matrix.
5. Record pass/fail per skill.

#### Phase C — Cross-Skill Coherency Checks

Execute all 7 checks from `references/cross-skill-checklist.md`:

**C1. Cross-reference integrity.**
For every skill that references another skill (by name or path):
1. Verify the referenced skill exists at the declared path.
2. Verify the referenced skill's scope includes the claimed capability.
3. Flag orphan skills (skills not referenced by any other skill or persona).

**C2. Term/definition consistency.**
For each shared term (Level 1–5, system, module, function, specification, artifact):
1. Collect all definitions across all skills.
2. Verify definitions are compatible (not contradictory).
3. Flag terms defined differently in different skills.

**C3. Entry→exit chain validation.**
For each skill-to-skill invocation (e.g., project-lifecycle Phase 1 invokes cmmi-process-level):
1. Extract the invoking skill's phase/task entry criteria.
2. Extract the invoked skill's ETVX entry criteria.
3. Verify the invoker's pre-conditions satisfy the invoked skill's entry criteria.
4. Verify the invoked skill's exit criteria and outputs satisfy the invoker's expected result.

**C4. Output path agreement.**
For each output path declared across skills:
1. Collect all path patterns (e.g., `projects/<project>/docs/reports/`).
2. Verify no two skills claim to produce the same filename at the same path.
3. Verify path conventions are consistent (all use `projects/<project>/docs/` prefix).

**C5. Document ID / baseline ID uniqueness.**
1. Collect all document IDs from YAML frontmatter across all skills.
2. Collect all baseline IDs from §1 across all skills.
3. Verify no duplicates exist.
4. Verify ID naming convention is consistent (SKILL-CMMI-XXX-NNN / BL-XXX-NNN).

**C6. README drift.**
1. Verify skill count in README matches actual `config/skills/` contents.
2. Verify each skill listed in README exists and vice versa.
3. Verify the dependency diagram matches actual skill references.
4. Verify the practice area table covers all practice areas cited in any skill.
5. Verify the audit section reflects the latest audit reports in `projects/cmmi/docs/audits/`.
6. Verify the directory tree matches the actual filesystem.

**C7. Metric framework coherency.**
1. Collect all KPIs from §5 of every CMMI skill.
2. Verify each KPI has a collection path.
3. Verify cmmi-glue's Workflow 4 (Continuous Improvement) is aware of metric sources from all skills.
4. Flag orphan metrics (KPIs defined in a skill but not referenced by any governance workflow).

#### Phase D — Report Generation

**D1. Aggregate findings.**
1. Classify each finding: Critical (blocks compliance), Major (significant gap), Minor (inconsistency), Observation (noted but no action).
2. Count findings by phase, severity, and skill.
3. Escalate Critical or Major process non-compliance against baselined skills via `cmmi-glue` Workflow 3 (SQA Audit & Non-Compliance Escalation) before closing the audit.

**D2. Produce unified report** at `projects/<project>/docs/audits/coherency-audit-<NNN>.md`:
1. Executive summary table (findings by severity).
2. Phase A results (per-skill, per-lens pass/fail matrix).
3. Phase B results (structural audit findings).
4. Phase C results (cross-skill coherency findings with evidence).
5. Phase D summary (README drift findings).
6. Remediation plan (ordered by severity, with file locations).

**D3. Fix actionable findings** (if authorized by the invoker).

#### Writing Constraints

| Rule | Requirement |
|---|---|
| Binary verdicts | Every check produces PASS or FAIL with evidence. No "partially compliant." |
| No false positives | Apply the established false-positive patterns (see §4.V) before reporting a finding. |
| Severity classification | Critical: blocks CMMI compliance. Major: significant gap. Minor: inconsistency. Observation: noted, no action. |
| Evidence required | Every FAIL must cite the file, line, and exact text that fails the check. |

### V — Verification & Validation

*Practice area: PQA SP 1.1 — objective evaluation of audit completeness.*

Before delivering the report, verify:

- [ ] Every skill in `config/skills/` was audited by all 4 lenses (A1–A4), with non-CMMI skills marked N/A where structural checks don't apply (unless tailored per §6).
- [ ] Every skill was checked for ETVX completeness (B2).
- [ ] `project-lifecycle` was checked for ETVX × V-Model compatibility (B1).
- [ ] All 7 cross-skill coherency checks (C1–C7) were executed (unless tailored per §6).
- [ ] README was verified for drift (C6) (unless tailored per §6).
- [ ] No known false-positive patterns were reported as findings:
    - Check 9 in polish-skill: absence of cautionary examples ≠ failure.
    - Banned terms in ban-rule text: self-referential listing is acceptable.
    - "Process Owner" in Approvals tables: generic CMMI term, not a RACI persona.
    - Non-CMMI skills (agent-project-structure, polish-skill, plantuml, system-design-paradigms): §1–§6 structural checks are N/A.
- [ ] Every finding has a severity classification and file-level evidence.
- [ ] The report is filed at the declared output path.

### X — Exit Criteria

- [ ] All V — Verification & Validation checks pass.
- [ ] The unified report exists with 0 unclassified findings.
- [ ] Every Critical and Major finding has a remediation entry.

### O — Outputs & Destinations

| Output | Format | Destination |
|---|---|---|
| Unified coherency audit report | Markdown | `projects/<project>/docs/audits/coherency-audit-<NNN>.md` |
| Per-skill pass/fail matrix | Table in report | Embedded in report §2 |
| Cross-skill coherency results | Table in report | Embedded in report §4 |
| Remediation plan | List in report | Embedded in report §6 |

---

## 5. Measurement and Metrics

*Practice area: MPM SP 1.1 — quantitative tracking of framework coherency.*

| KPI | Formula | Collection Point | Organisational Objective |
|---|---|---|---|
| Overall pass rate | (total checks passing) / (total checks run) × 100 | Audit report | >95% framework pass rate |
| Cross-skill coherency score | (C-checks passing) / 7 × 100 | Audit report §4 | 100% cross-skill coherency |
| Intra-skill compliance rate | (lens checks passing) / (lens checks run) × 100, per lens | Audit report §2 | 100% per-lens compliance |
| README accuracy score | (README checks passing) / (README checks run) × 100 | Audit report C6 | 100% README accuracy |
| Finding resolution rate | (findings fixed) / (findings reported) × 100 | Post-remediation re-run | 100% Critical + Major resolved |
| Audit coverage | (skills audited) / (total skills) × 100 | Audit report | 100% coverage |

### Metric Collection Path

All coherency audit metrics are collected in:
`projects/<project>/docs/audits/coherency-audit-<NNN>.md`

The EPG Lead reviews metrics after each audit run. Trends across audit runs
feed into `cmmi-glue` Workflow 4 (Continuous Improvement).

### Governance Review Cadence

Run the coherency audit after any structural change to the skill library
(new skill added, skill modified, persona changed, README updated). The
EPG Lead reviews the report and authorizes remediation.

---

## 6. Tailoring Guidelines

*Practice area: OPD SP 1.1 — controlled adaptation of the audit scope.
All deviations follow `cmmi-glue` Workflow 1 (Tailoring Process).*

| Deviation | Conditions for Approval | Approval Authority |
|---|---|---|
| Skip Phase A lenses for unchanged skills | No modifications since last audit pass | SQA Auditor |
| Skip Phase B structural audit | project-lifecycle has not been modified since last audit | SQA Auditor |
| Skip Phase C cross-skill checks | No new skills added or removed since last audit | EPG Lead |
| Skip Phase D README verification | README has not been modified and no new skills added | SQA Auditor |
| Run only Phase C (cross-skill only) | Quick coherency check after a targeted skill edit | SQA Auditor |
| Skip fix phase (D3) | Audit is for assessment only; fixes will be done separately | EPG Lead |
| Profile S audit scope: skip A3, A4, B1, C4–C7 | Project uses Profile S tailoring | SQA Auditor |
| Profile M audit scope: skip A4 | Project uses Profile M tailoring | SQA Auditor |
| Profile L: full audit required | Project uses Profile L tailoring | No deviation — run all phases |
| **Profile-P audit scope** | Skip A1–A4 lens checks for the 8 `pycsl-*` domain skills (`pycsl-annotate`, `pycsl-doc-coherency`, `pycsl-docs`, `pycsl-exception-model`, `pycsl-how-to-develop`, `pycsl-software-architecture`, `pycsl-stdlib-coverage`, `pycsl-ub-catalog`) — they are domain skills, not process skills; coherency is enforced by `bin/doc-coherency.py --check`. Run a new **C8 spec-mirror + Squeeze coverage check** (implemented as `bin/cmmi-audit.sh`) that verifies: (1) no `BL/.../src/` dirs exist; (2) `bin/cmmi-include-expand.py --verify` passes; (3) `bin/cmmi-mod-index.py --verify` reports per-System index ↔ def-count parity; (4) `PROJECT.md` `squeeze_owners:` block names ≥1 System per Squeeze S1–S9 and every non-glue System owns ≥1 Squeeze. | Project uses Profile-P (PyCSL); single-developer CCB |

### Profile-Aware Audit Scope

When auditing a project (not the skill library itself), the audit scope is
determined by the project's tailoring profile declared in `PROJECT.md`.
See `config/skills/project-lifecycle/references/tailoring-profiles.md` for the full
audit scope matrix per profile.

All tailoring deviations must be recorded in the audit report under a
"Tailoring Deviations" section.

---

*This document is a Configuration Item (CI) under baseline BL-COHER-001.
Changes require Change Control Board approval per `cmmi-glue` Workflow 2.*
