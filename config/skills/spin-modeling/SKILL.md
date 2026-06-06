---
name: spin-modeling
description: >-
  Use Spin and Promela to model concurrent coordination, verify deadlock freedom,
  diagnose counter-examples, and check assertion and LTL properties in system-
  and component-level designs. Use when the user needs to verify concurrency
  properties, replay counter-examples, or add safety/liveness checks to a model.
document_id: SKILL-SPIN-001
version: "1.0"
status: Approved
effective_date: "2026-05-29"
baseline_id: BL-SPIN-001
cmmi_version: "2.0"
practice_areas:
  - "RDM SP 1.1 — Maintain Bidirectional Traceability"
  - "PQA SP 1.1 — Objectively Evaluate Processes"
---
# Spin / Promela Modeling
## 1. Document Control & Metadata
| Field | Value |
|---|---|
| Document ID | SKILL-SPIN-001 |
| Version | 1.0 |
| Status | Approved |
| Effective Date | 2026-05-29 |
| Classification | Configuration Item (CI) — baseline BL-SPIN-001 |
### Revision History
| Version | Date | Description of Change | Author |
|---|---|---|---|
| 1.0 | 2026-05-29 | Restructured to CMMI §1–§6 + Extended ETVX; separated canonical example from anti-pattern | — |
### Approvals
| Name | Role | Date |
|---|---|---|
| *(EPG Lead)* | Accountable | — |
| *(SQA Auditor)* | Verification authority | — |
| *(System Architect / Technical Lead)* | Consulted | — |
---
## 2. Introduction & Context
### 2.1 Purpose
*Practice areas: RDM SP 1.1 — maintains traceability between coordination scenarios, abstractions, and verified properties; PQA SP 1.1 — defines objective checks for model quality and verification evidence.*
This skill standardises Spin / Promela modelling for concurrency-focused verification:
- **Deadlock at System level.** Verify multi-system coordination before integration.
- **Delegation deadlock.** Verify lower-level coordination created by delegation to sub-actors.
- **Diagnosing reported failures.** Reproduce hangs and analyse reachable deadlocks from a suspected state.
### 2.2 Scope
| In Scope | Out of Scope |
|---|---|
| System-level coordination models for deadlock and safety analysis | Questions about functional intent rather than process interference |
| Component-level coordination models involving channels, shared state, or ordering constraints | Single-threaded systems with no concurrent interleavings |
| Counter-example replay and property-oriented debugging | Full-system models with no defensible abstraction boundary |
### 2.3 Audience
- System Architects authoring System-level coordination models.
- Technical Leads authoring Component-level coordination models.
- SQA Auditors reviewing verification evidence.
- Software Engineers consulted on implementation details reflected in the abstraction.
### 2.4 References & Definitions

| Term | Definition |
|---|---|
| Spin | Model checker for concurrent systems |
| Promela | Process Meta Language used by Spin |
| `d_step` | Deterministic atomic block; no statement inside may block |
| LTL | Linear Temporal Logic used for liveness and ordering properties |
| CI | Configuration Item baselined under configuration management |

### References

| Reference | Location |
|---|---|
| Promela syntax and primitives | `references/promela-basics.md` |
| Guarded `d_step` modelling pattern | `references/modeling-discipline.md` |
| Verification commands and trail replay | `references/verification-workflow.md` |
| Channels and coordination patterns | `references/channels-and-coordination.md` |
| Assertions and LTL properties | `references/properties.md` |
| Methodology integration and worked cases | `references/methodology-integration.md` |

### Referenced Skills

| Skill | Usage |
|---|---|
| `cmmi-glue` | Workflow 1 approvals for tailoring; Workflow 3 escalation for non-compliance |
---
## 3. RACI Matrix

*Practice area: PQA SP 1.1 — ensures each modelling activity has clear accountability.*

| Task | System Architect | Technical Lead | EPG Lead | SQA Auditor | Software Engineer |
|---|---|---|---|---|---|
| Select System-level abstraction and model scope | R | I | A | C | C |
| Select Component-level abstraction and model scope | I | R | A | C | C |
| Author or update Promela model | R | R | A | C | C |
| Define properties and acceptance criteria | R | R | A | C | C |
| Execute Spin verification and replay counter-examples | C | C | A | R | C |
| Review evidence and approve tailoring decisions | I | I | A | R | I |
---
## 4. Process Architecture (Extended ETVX Model)

*Practice areas: RDM SP 1.1 — maintains traceability from coordination risks to verified properties;
PQA SP 1.1 — defines objective checks for model quality and verification evidence.*

### E — Entry Criteria
- [ ] Concurrency or coordination risk has been identified.
- [ ] The property to verify is stated in operational terms.
- [ ] An abstraction boundary is defined.
- [ ] Responsible and Accountable roles are assigned per §3.
### I — Inputs & Sources
| Input | Source | Format |
|---|---|---|
| Coordination scenario or failure report | Design package, incident record, or user request | Text / diagram |
| Candidate abstraction | System Architect or Technical Lead | State and channel sketch |
| Property list | Architect, Lead, or verifier | Deadlock, assertion, or LTL list |
| Modelling references | `references/` | Markdown |
| Tailoring decisions, if any | `cmmi-glue` Workflow 1 output | Approved record |
### T — Tasks / Activities
**Key concept — guarded `d_step`:** Model each transition as one guarded `d_step` whose precondition guarantees the body cannot block. Use `references/modeling-discipline.md` for the full pattern and exceptions.
1. **Pick the right abstraction.** Define processes, local state, shared state, and channels. Model coordination only; omit computation not required for the property. See `references/channels-and-coordination.md`.
2. **Write the Promela.** Implement one `proctype` per actor type and one guarded `d_step` per transition. Use `references/promela-basics.md` and `references/modeling-discipline.md`.
3. **Verify the model.** Run Spin generation, compile `pan`, execute verification, and replay any trail. Use `references/verification-workflow.md`.
4. **Add properties beyond deadlock.** Encode assertions or LTL formulas for ordering, mutual exclusion, response, or liveness. Use `references/properties.md`.
#### Writing Constraints
| Rule | Requirement |
|---|---|
| Model coordination, not computation | Represent internal work as a single transition unless it changes the verified property |
| One guarded transition per state change | Use one guarded `d_step` per transition; justify any exception from `references/modeling-discipline.md` |
| Scale by controlled abstraction | Start with the smallest process set that exercises the property; expand only when evidence requires it |
| Treat deadlocks as findings | Replay every invalid end state and resolve it by correcting the model, the design, or the property set |
| Verify explicit properties | Deadlock freedom is the default minimum; add assertions or LTL for material risks |
#### Correct Example
**Buffered channel example with a non-blocking send guard:**
```promela
mtype = { req };
chan a_to_b = [1] of { mtype };
bool a_done = false;
bool b_seen = false;
active proctype A() {
  do
  :: !a_done && nfull(a_to_b) -> d_step { a_to_b ! req; a_done = true; }
  :: else -> break
  od
}
active proctype B() {
  do
  :: !b_seen && len(a_to_b) > 0 -> d_step { a_to_b ? req; b_seen = true; }
  :: else -> break
  od
}
```
#### Common Pitfalls
**Anti-pattern — blocking rendezvous send inside `d_step`:**
```promela
mtype = { req };
chan a_to_b = [0] of { mtype };
bool a_done = false;
active proctype A() {
  do
  :: !a_done -> d_step { a_to_b ! req; a_done = true; }
  od
}
```
This anti-pattern is invalid because the send can block; correct it before verification.
### V — Verification & Validation
- [ ] Entry criteria were satisfied before modelling began.
- [ ] Every task in §4.T maps to §3 roles.
- [ ] Every transition is guarded or explicitly justified by the modelling discipline reference.
- [ ] Verification evidence exists for deadlock checking and any declared safety or LTL properties.
- [ ] Counter-examples were replayed and dispositioned.
- [ ] Tailoring decisions, if used, were approved per `cmmi-glue` Workflow 1.
- [ ] Non-conformances are escalated per `cmmi-glue` Workflow 3.
### X — Exit Criteria
- [ ] All V — Verification & Validation checks pass.
- [ ] The model and property set are traceable to the analysed coordination scenario.
- [ ] Verification evidence is stored with the model output.
- [ ] The Accountable role has reviewed the result.
### O — Outputs & Destinations
| Output | Format | Destination |
|---|---|---|
| Promela model | `.pml` | Project formal-verification or specification repository |
| Verification evidence | Command log, trail replay, or summary | Project QA / verification evidence store |
| Property catalogue | Markdown or specification annex | Attached to the model or governing design artifact |
---
## 5. Measurement and Metrics

*Practice area: MPM SP 1.1 — quantitative tracking of verification effectiveness.*

| KPI | Formula | Collection Point | Organisational Objective |
|---|---|---|---|
| State space size | `(states explored / memory limit) × 100` | Per verification run | Keep verification tractable (<10M states) |
| Property coverage | `(properties verified / properties identified) × 100` | Per model | 100% property coverage |
| Counter-example resolution rate | `(counter-examples resolved / counter-examples found) × 100` | Per project | 100% resolution |

### Metric Collection Path

All spin-modeling metrics are collected per verification run and aggregated at
the project level in `projects/<project>/docs/reports/`. The Metrics Analyst
consumes these via `cmmi-metrics-collection` and `cmmi-glue` Workflow 4
(Continuous Improvement).

---
## 6. Tailoring Guidelines

*Practice area: OPD SP 1.1 — controlled adaptation of the modelling process.
All deviations follow `cmmi-glue` Workflow 1 (Tailoring Process).*
| Allowed Deviation | Condition | Approval Authority |
|---|---|---|
| Skip Spin modelling | System is single-threaded and has no concurrency | Technical Lead |
| Deadlock-only verification | Coordination is low complexity and LTL properties are not justified | SQA Auditor |
| Model only critical paths | System contains more than 20 interacting processes | EPG Lead |
*This document is a Configuration Item (CI) under baseline BL-SPIN-001.
Changes require Change Control Board approval per `cmmi-glue` Workflow 2.*
