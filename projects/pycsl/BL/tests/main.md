# BL — Business Level Test Plan (PyCSL)

**Document ID:** TEST-PYCSL-BL-001
**Profile:** P
**Layer:** L1 (Business — UAT-equivalent for a CMMI L1)
**Owner:** UAT Test Engineer role bound to `bin/run-reference-tests.sh`

---

## Acceptance tests (BL-AT-NNN)

The BL passes when the four acceptance criteria from
[`../specifications/main.md`](../specifications/main.md) all hold.
Each criterion maps to a concrete test command:

| Test ID | Acceptance criterion | Command | Status |
|---|---|---|---|
| BL-AT-001 | S2 squeeze proves at scale (≤ 2 axioms) | `cd src/formal-semantics/rocq && coqc -batch Phase8_Soundness.v && grep 'Axiom' < Phase8_Soundness.glob \| wc -l` | running |
| BL-AT-002 | S5 squeeze converges (zero unreconciled cross-prover pairs) | `bin/check-proof-crosscheck.sh` | running |
| BL-AT-003 | S4 squeeze closes the loop (self-annotation suite passes) | `bin/run-self-annotation-suite.sh` | partial — `errors.py` only |
| BL-AT-004 | S9 squeeze trends down (auto-trust count monotonically non-increasing) | per-release auto-trust count snapshot vs. previous release | tracked via `bin/cmmi-metrics-ingest.py` |

These are long-arc tests. See `csl-from-scratch` §15 and the
per-system test plans under
`BL/SY<N>-<Name>/tests/main.md` for the per-System acceptance test
suites that feed into the BL aggregate.

---

## Regression test for the framework itself

| Test ID | Scenario | Expected |
|---|---|---|
| BL-AT-REG-001 | Replay the 2026-05-31 13:47:22 `itertools.cycle` L3-ceiling fallback through the tailored pipeline. | The SY3-Pycsl Reconciliator (`agent-feature-supervisor.py`) classifies the gap as `iterator-semantics`, increments the counter in `metrics/stdlib-gap-report.json`, and (with `--proposal-threshold 1`) auto-drafts a `missing-iterator-semantics-feature.md` proposal into `proposed-features/`. Snapshot fixture frozen at `test-suite/cmmi-regression/fixtures/itertools-incident-snapshot.py`. **STATUS: PASSING** (per `bin/cmmi-audit.sh [REG]` check, Item 2 landed). |

The test is now wired into `bin/cmmi-audit.sh` as the `[REG]` step
and runs `pytest test-suite/cmmi-regression/` on every audit. It is
the acceptance criterion the user explicitly asked for in the CMMI
tailoring discussion: *"agents should now spot what only the human
spotted before."*
