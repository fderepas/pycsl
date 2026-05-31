# Lessons Learned from skill2rag Pilot Import

*Reference document for `import-existing-code` (SKILL-IMPORT-001).*
*Extracted from pilot import of `src/skill2rag/` — all gaps are now addressed
as mandatory steps in the parent skill.*

---

## 1. Gaps Found

| # | Gap | Severity | Where It Matters |
|---|---|---|---|
| G1 | **No PlantUML diagrams** generated | Major | L2 system spec has ASCII art instead of proper UML |
| G2 | **No RACI matrices** in specs | Major | Cannot determine who is responsible for what |
| G3 | **No formal CMMI documents** (BRD, SRS, SAD, HLD, MLD, LLD) | Major | Specs exist but not in the `cmmi-documents` format |
| G4 | **No traceability matrix** linking specs ↔ tests | Major | Cannot prove test coverage against requirements |
| G5 | **No SQA summary report** — test results only in commit message | Major | No persistent, auditable test summary document |
| G6 | **Communication skill not used** — no tracked message exchanges | Minor | Inter-agent coordination was informal |
| G7 | **No metrics collection** per `cmmi-metrics-collection` | Minor | KPIs not recorded |
| G8 | **`__init__.py` package shadowing** in test layout | Minor | Tests passed individually but failed combined |
| G9 | **No `pyproject.toml`** — manual venv setup required | Minor | No reproducible build/test environment |
| G10 | **Parallelized levels without strict ordering** — L5→L1 ran simultaneously | Obs | Acceptable for retro-spec (code is source of truth) but inappropriate for greenfield |

---

## 2. What Worked Well

- Bottom-up retro-specification accurately captured existing behavior.
- Parallel agent dispatch for independent work (6 spec agents, 5 test agents).
- Test fixtures with deterministic fake embeddings enabled fully offline testing.
- Mocking strategy (only mock external I/O) gave real integration coverage.
- 111 tests all passing in 0.48s — fast feedback loop.

---

## 3. Remediation Checklist

For a fully CMMI-compliant import, verify these steps after Phase 3:

- [ ] Run `plantuml` skill to generate diagrams for L2–L4 specs.
- [ ] Run `cmmi-documents` skill to formalize each spec into the proper document type.
- [ ] Build a traceability matrix (requirements → specs → tests → results).
- [ ] Create `communication` message-queue entries for inter-level hand-offs.
- [ ] Collect metrics per `cmmi-metrics-collection` (test counts, coverage, defect density).
- [ ] Generate SQA summary report under `projects/<name>/docs/reports/`.
- [ ] Create `pyproject.toml` with test dependencies.
