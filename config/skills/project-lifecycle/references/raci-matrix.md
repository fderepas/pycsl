# RACI Matrix

*Practice area: OPD SP 1.1 — role-to-level mapping for the project lifecycle.*

| Level / Phase | Activity | Business Analyst / Product Owner² | EPG Lead | System Architect | Project Manager | EPG Member | Configuration Manager | UAT Test Engineer | Reconciliator | Technical Lead | System Test Engineer | Integration Test Engineer | Software Engineer | Module Test Engineer | Unit Test Engineer | SQA Auditor | Metrics Analyst | All stakeholders¹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Phase 1 | Gap Analysis | R | A | C | I | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Phase 2 | Process Documents | — | A | — | I | R | C | — | — | — | — | — | — | — | — | — | — | — |
| Business | Specify (BRD, system decomposition, coordination spec) | R, A | I | C | — | I | C | — | — | — | — | — | — | — | — | C | I | — |
| Business | Define test plan (UAT) | A | — | — | — | — | — | R | — | — | — | — | — | — | — | C | — | — |
| Business | Reconcile failures | A | I | — | — | — | — | C | R | — | — | — | — | — | — | I | — | — |
| System | Specify (SRS/SAD/ICD, component decomposition, coordination spec) | — | I | R, A | — | I | C | — | — | C | — | — | — | — | — | C | I | — |
| System | Define test plan (system + integration tests) | — | — | A | — | — | — | — | — | — | R | C | — | — | — | C | — | — |
| System | Reconcile failures | — | — | A, C | — | — | — | — | R | — | C | — | — | — | — | I | — | — |
| Component | Specify (HLD, module decomposition, coordination spec) | — | — | — | — | — | C | — | — | R, A | — | — | C | — | — | C | I | — |
| Component | Define test plan (component integration tests) | — | — | — | — | — | — | — | — | A | — | R | — | — | C | C | — | — |
| Component | Reconcile failures | — | — | — | — | — | — | — | R | A, C | — | C | — | — | — | I | — | — |
| Module | Specify (MLD, unit decomposition, coordination spec) | — | — | — | — | — | C | — | — | A | — | — | R | — | — | C | I | — |
| Module | Define test plan (module tests) | — | — | — | — | — | — | — | — | A | — | — | C | R | — | C | — | — |
| Module | Reconcile failures | — | — | — | — | — | — | — | R | A | — | — | C | C | — | I | — | — |
| Unit | Specify (LLD, formal annotations, pre/post-conditions) | — | — | — | — | — | C | — | — | A | — | — | R | — | — | C | I | — |
| Unit | Define test plan (unit tests / proofs) | — | — | — | — | — | — | — | — | A | — | — | C | — | R | C | — | — |
| Unit | Reconcile failures | — | — | — | — | — | — | — | R | A | — | — | C | — | C | I | — | — |
| Phase 10 | Implement code (Coder + Validator) | — | — | — | — | — | I | — | — | A | — | — | R | — | — | — | — | — |
| Phase 12 | Final Audit | — | A | — | — | — | — | — | — | — | — | — | — | — | — | R | C | I |

¹ Broadcast notification pattern — not a single persona.
² Combined persona: `config/agents/business-analyst.md` (role: Business Analyst / Product Owner).

**Orchestration tasks (§4.T mapping):**

| Task | Activity | EPG Member | EPG Lead | Configuration Manager | Project Manager | Business Analyst | UAT Test Engineer | Reconciliator | System Architect | System Test Engineer | Technical Lead | Integration Test Engineer | Software Engineer | Module Test Engineer | Unit Test Engineer | SQA Auditor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | Project Initialisation | R | A | C | I | — | — | — | — | — | — | — | — | — | — | — |
| T2 | Execute Business Level | — | A | — | — | R | R | R | — | — | — | — | — | — | — | — |
| T3 | Execute System Level | — | — | — | — | — | — | R | R, A | R | — | — | — | — | — | — |
| T4 | Execute Component Level | — | — | — | — | — | — | R | — | — | R, A | R | — | — | — | — |
| T5 | Execute Module Level | — | — | — | — | — | — | R | — | — | A | — | R | R | — | — |
| T6 | Execute Unit Level | — | — | — | — | — | — | R | — | — | A | — | R | — | R | — |
| T7 | Phase 10 — Code + Validate (leaf) | — | — | I | — | — | — | — | — | — | A | — | R | — | — | — |
| T8 | Level Transition and Delegation Rules | R | A | — | — | — | — | — | — | — | — | — | — | — | — | C |
