# Agent-ecosystem KPIs — CMMI Level-4 catalog (Profile-P)

This catalog defines the **Level-4 (Quantitatively Managed)** metrics for the PyCSL
agent ecosystem: which signals are worth tracking, their formulas, where they come
from, and how they become statistically-managed objectives. It is the agent-loop
companion to the per-system KPIs in `cmmi-metrics-collection/SKILL.md` §6 (Profile-P).

**Sources.** Each run emits a machine-readable summary; `bin/cmmi-metrics-ingest.py`
rolls them into `projects/pycsl/docs/metrics/metrics-store.json` under
`global.agent_loop_kpis`:
- `metrics/run-summary/<file>.json` — `coordinator.py` per file (annotation-loop axis).
- `metrics/feature-supervisor/<slug>/run-summary.json` — `agent-feature-supervisor`
  per invocation (feature-rollout axis).

**QPPO method (all KPIs).** Record-only until `cmmi-metrics-ingest.py --weekly` has
≥8 snapshots; then `cmmi-quantitative-mgmt` computes the process-performance baseline
(μ, σ), control limits `UCL=μ+3σ / LCL=max(0,μ−3σ)`, and replaces any qualitative
target with a statistically-grounded objective (e.g. `μ−1σ`). **No fixed numeric
targets before a baseline exists.** L4 *detects* out-of-control points (Western
Electric rules); diagnosing *why* and changing the process is **L5 CAR** — out of scope.

**Two axes.** The annotation-loop axis is exercised by `coordinator.py` runs (the
annotate→prove→reconcile pipeline). The feature-rollout axis is exercised by
`agent-feature-supervisor` runs (e.g. `--feature-file 16-steps-exec.md`). A supervisor
run does **not** populate the annotation-loop KPIs, and vice-versa.

## Family 1 — Inter-agent loop efficiency
| KPI | Formula | Axis |
|---|---|---|
| Annotation convergence | attempts-to-green per file (μ, σ, max) | annotation |
| Loop-detection rate | (exit-73 loop-detected + ping-pong halts) / files | annotation |
| Re-decomposition rate | Σ redecompose_count / files (L5→L4 escalations) | annotation |
| Delegation rollback rate | rolled-back / delegated phases | rollout |
| Load-bearing halt rate | load-bearing halts / runs | rollout |

## Family 2 — Reconciliation diagnostic accuracy (annotation axis; downstream proxy)
| KPI | Formula |
|---|---|
| Fault-attribution correctness | per `fault_class` F and overall: P(next proof passes \| classified F, action taken) |
| First-fix yield | files green on the first attempt after the first reconcile / files needing reconcile |
| Fault-class distribution | counts of sub-actor / specifier / verifier (feeds L5 CAR) |

> **Proxy caveat.** "Correctness" here is a **joint** diagnostic+repair signal — a
> recommendation is scored right iff its routed action (`sub-actor`→`agent-script-update`,
> `specifier`→`agent-splitter` re-decompose) made the *next* attempt's proof pass. It
> conflates classification quality with fix quality. To isolate pure classification
> accuracy, add an optional labeled spot-check audit later to calibrate the proxy.

## Family 3 — Rocq proof difficulty / "ease"
| KPI | Formula | Axis |
|---|---|---|
| Rocq completion rate | `.v` completed / `.v` generated | annotation |
| Retries-per-obligation | `agent-rocq-proof-writer` attempts used per `.v` (μ, σ; 1–3) | annotation |
| Abort rate | provably-unprovable (`Abort`) / obligations | annotation |
| Rocq-citation density | `#@ proof rocq`/`lean` lines in a phase's stubs (with the 0-`\trusted` check) | rollout |

## Governance / quality (cross-cutting; partly pre-existing)
| KPI | Formula | Source |
|---|---|---|
| NCR rate + open-NCR age | Workflow-3 NCRs / runs; max age of OPEN | `metrics/ncr/*` |
| Gate pass-rate per step | passed / (passed+failed) non-skipped gate steps | feature run-summary `gate` |
| Acceptance pass-rate | claims passed / total across phases | feature run-summary |
| STATUS_FORGED rate | runs halted STATUS_FORGED / runs (a DONE phase whose claim now fails) | feature run-summary |
| Fix efficacy | evaluator `resolution_status` ∈ {Success, Partial, Regression} rates | `metrics/evaluator/*.json` |
| Human-intervention rate | `requires_human_intervention=true` / reviews | `metrics/reviewer/*.json` |

## Where these land in the store
`metrics-store.json → latest.global.agent_loop_kpis`:
- `annotation_loop`: `convergence_attempts{avg,max,samples}`, `loop_detect_rate`,
  `redecompose_rate`, `first_fix_yield`, `fault_correctness{by_class,overall}`,
  `rocq{completion_rate,abort_rate,retries}`.
- `feature_rollout`: `acceptance_passrate`, `gate_passrate`,
  `delegation_rollback_rate`, `loadbearing_halt_rate`, `status_forged_rate`,
  `rocq_citations`.

See `config/schemas/run-summary.schema.json` and
`config/schemas/feature-run-summary.schema.json` for the emitted shapes.
