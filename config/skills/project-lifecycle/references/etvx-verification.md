# ETVX — Verification, Exit Criteria, and Outputs

These are the V, X, and O sections of the Process Architecture
(Extended ETVX Model) defined in `SKILL.md` §4. They are the
end-of-lifecycle checklists and the output destination map;
consult them when closing out a project lifecycle or when
locating where a lifecycle artifact must be written.

## V — Verification & Validation

*Practice area: PQA SP 1.1 — objective evaluation of lifecycle adherence.*

Before marking a project lifecycle as complete, verify:

- [ ] Phase 1 (Gap Analysis) and Phase 2 (Process Documents) have been executed.
- [ ] All in-scope specification levels have completed their execution cycle (Synchronize → Delegate → Sub-actors Work → Run Tests → Reconcile).
- [ ] Delegation fan-out was executed for all sub-units at each level (all systems, components, modules, units).
- [ ] Level entry/exit criteria were checked and recorded at each transition.
- [ ] The independence constraint was respected (Specifier ≠ Verifier ≠ Reconciliator at each level) (unless tailored per §6).
- [ ] Coordination specs exist at every level and were validated against test failures.
- [ ] All reconciliation loops terminated (either tests pass or escalation was triggered).
- [ ] Cross-level reconciliation routing was correctly applied (sub-actor faults escalated downward; Specifier faults escalated upward when warranted).
- [ ] The directory hierarchy follows the prescribed naming convention (`BL/SY<N>-<Name>/CO<N>-<Name>/MO<N>-<Name>/UN<N>-<Name>/`) per `references/directory-hierarchy.md`.
- [ ] Every level directory contains `requirements/`, `specifications/`, and `tests/` subdirectories with populated `main.md` files.
- [ ] `src/` directories exist at CO, MO, and UN levels (or at the deepest in-scope level per tailoring profile).
- [ ] A Requirements Traceability Matrix (RTM) links all in-scope levels.
- [ ] The final gap re-run (Phase 12) shows 0 Critical and 0 Major gaps (unless tailored per §6).
- [ ] All test suites pass at all in-scope levels.
- [ ] The SQA audit report is filed with 0 open NCRs (non-conformances are escalated via `cmmi-glue` Workflow 3).
- [ ] Reconciliation logs exist for each level where re-work occurred.

## X — Exit Criteria

- [ ] All V — Verification & Validation checks pass.
- [ ] The project's success criteria (from PROJECT.md) are met.
- [ ] The EPG Lead has approved the lifecycle completion.

## O — Outputs & Destinations

| Output | Format | Destination |
|---|---|---|
| Gap analysis report | Markdown | `projects/<project>/docs/reports/` |
| Process documents (QA plan, CM procedure) | Markdown | `projects/<project>/docs/process/` |
| Requirements (per-level) | Markdown | `projects/<project>/BL/.../requirements/main.md` |
| Specifications (per-level) | Markdown | `projects/<project>/BL/.../specifications/main.md` |
| Test plans and test results (per-level) | Markdown | `projects/<project>/BL/.../tests/main.md` |
| Source code | Source code | `projects/<project>/BL/.../src/` (CO, MO, UN levels) |
| Reconciliation logs | Markdown | `projects/<project>/docs/reports/` |
| RTM | Markdown | `projects/<project>/docs/reports/` |
| SQA audit report | Markdown | `projects/<project>/docs/audits/` |
| Metrics report | Markdown | `projects/<project>/docs/reports/` |
