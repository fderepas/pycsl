# CMMI Level-4 metrics for the PyCSL agent ecosystem

> On approval, copy this plan to repo-root `cmmi-l4-metrics-plan.md`, then execute.

## Context

You're about to run `agent-feature-supervisor --allow-load-bearing --feature-file
16-steps-exec.md` and asked which metrics are worth tracking for **CMMI Level 4
(Quantitatively Managed)** — loops between agents, whether reconciliation agents
spot the right cause, ease of writing Rocq proofs.

The L4 *machinery* already exists and should be reused, not rebuilt:
- `config/skills/cmmi-quantitative-mgmt/` — PPB (μ/σ), control limits `UCL=μ+3σ /
  LCL=max(0,μ−3σ)`, SPC charts, Western Electric out-of-control rules, QPPOs.
  **L4 detects out-of-control; root-cause + process change is L5 CAR (out of scope).**
- `config/skills/cmmi-metrics-collection/` + `bin/cmmi-metrics-ingest.py` →
  `projects/pycsl/docs/metrics/metrics-store.json` (`latest` + `snapshots[]`).
  Profile-P already defers chart generation until `--weekly` has **≥8 snapshots**
  and names a few KPIs (L3-ceiling rate, Reconciliator-escalation rate, spec-mirror drift).

**The gap:** the rich signals the agents emit (exit codes 72/73/74/75, `fault_class`,
NCRs, redecompose counts, evaluator/monitor/reviewer JSON, Rocq completion, supervisor
per-phase acceptance/gate/delegation outcomes) are scattered across logs and never
captured as a structured **per-run summary**, and there's no catalog tying them to
QPPOs. Also, your three families span **two axes**:
- **Annotation-loop axis** (`coordinator.py`): reconciliation right-cause, Rocq ease,
  retry/loop drift. **Not exercised by the 16-steps run.**
- **Feature-rollout axis** (`agent-feature-supervisor`, the 16-steps run): per-phase
  acceptance/gate pass-rates, delegation iterations/rollback, load-bearing halts, and
  Rocq-citation difficulty for the no-`\trusted` stubs.

**Outcome:** each run emits a machine-readable run-summary; `cmmi-metrics-ingest.py`
rolls them into `metrics-store.json`; a catalog defines the L4 metric set + QPPO
method; SPC charts auto-generate once ≥8 weekly snapshots exist (existing deferred
mode). The 16-steps run becomes the **seed datapoint** for the feature-rollout axis.

## Decisions (from clarifying questions)
- **Full instrumentation**: coordinator + supervisor emit per-run summary JSON.
- **Reconciliation right-cause = downstream proxy** (automatic, no labels).
- **Both axes**, clearly separated.

## The metric catalog (the answer: which metrics are worth tracking)

QPPO method for every metric (per Profile-P): **record-only until ≥8 weekly
snapshots**, then `cmmi-quantitative-mgmt` computes μ±3σ control limits and replaces
qualitative targets with statistically-grounded objectives (e.g. `μ−1σ`). No arbitrary
numeric targets before a baseline exists.

### Family 1 — Inter-agent loop efficiency
| KPI | Formula | Source | Axis |
|---|---|---|---|
| Annotation convergence | attempts-to-green per file (μ,σ) | coordinator run-summary | A |
| Loop-detection rate | exit-73 halts / files processed | run-summary / NCR | A |
| Re-decomposition (L5→L4) rate | redecompose events / proof failures; ping-pong cap-hits / files | run-summary | A |
| Delegation iterations | attempts to gate-green per phase (μ,σ) | feature run-summary | B |
| Delegation rollback rate | rolled-back / delegated phases | feature run-summary | B |

### Family 2 — Reconciliation diagnostic accuracy (axis A; downstream proxy)
| KPI | Formula | Source |
|---|---|---|
| Fault-attribution correctness | per `fault_class` F: P(next proof passes \| classified F, action taken) | run-summary fault→outcome linkage |
| First-fix yield | files green on the 1st attempt after first reconcile / files needing reconcile | run-summary |
| Fault-class distribution | counts of sub-actor / specifier / verifier | run-summary (feeds L5 CAR) |
| Fix efficacy | evaluator `resolution_status` ∈ {Success, Partial, Regression} rates | `metrics/evaluator/*.json` (exists) |

> *Proxy caveat (state honestly in the catalog):* "correctness" here is a **joint**
> diagnostic+repair signal (classified-F **and** the routed fix converged). To isolate
> pure classification accuracy, an optional labeled spot-check audit can be added later
> to calibrate the proxy — deferred, not in this plan.

### Family 3 — Rocq proof difficulty / "ease"
| KPI | Formula | Source | Axis |
|---|---|---|---|
| Rocq completion rate | `.v` completed / `.v` generated | coordinator `attempt_rocq_proof` | A |
| Retries-per-obligation | rocq-proof-writer attempts used per `.v` (μ,σ; 1–3) | rocq-proof-writer | A |
| Abort rate | provably-unprovable (`Abort`) / obligations | rocq-proof-writer | A |
| Rocq-citation density | `#@ proof rocq` lines per stub that reached 0-`\trusted` | feature run-summary | B |

### Governance / quality (cross-cutting; partly already emitted)
| KPI | Formula | Source |
|---|---|---|
| NCR rate + open-NCR age | Workflow-3 NCRs / runs; max age of OPEN | `metrics/ncr/*` |
| Gate pass-rate per step | passed / (passed+failed) per gate step | feature run-summary |
| Acceptance pass-rate + STATUS_FORGED rate | claims passed / total; DONE-but-now-fails / DONE | feature run-summary |
| Human-intervention rate | `requires_human_intervention=true` / reviews | `metrics/reviewer/*.json` (exists) |

## Part 1 — Instrumentation (emit per-run summaries)

### A. Coordinator (`src/pycsl/agents/coordinator.py`)
- New `config/schemas/run-summary.schema.json`.
- Accumulate a per-attempt record list per file inside `run()`: `{attempt, pycsl_pass,
  reconcile:{target, fault_class, rec_key}, action:{kind: script-update|redecompose|none,
  success}}`. The **fault→outcome proxy**: when attempt *i+1* runs `run_pycsl_file`,
  mark attempt *i*'s recommendation `right_cause = (attempt i+1 passed)`.
- New `write_run_summary(...)` → `metrics/run-summary/<stem>.json`, called on the
  success `break`, the exit-72 block, and the exit-73 block (reuse the loop state +
  `_redecompose_count`). Validate via `schema_validator.validate_or_warn(..., "run-summary")`.
- `attempt_rocq_proof`: record per-`.v` `{retries_used, status: completed|aborted|incomplete}`
  into the summary (needs rocq-writer to surface retries — below).

### A′. Rocq writer (`src/pycsl/agents/agent-rocq-proof-writer.py`)
- It already loops `MAX_RETRIES=3` and exits 0=completed / 1=abort-or-exhausted. Emit
  the attempt count + terminal status as a parseable marker on stdout (e.g.
  `ROCQ-SUMMARY {"retries":N,"status":"completed"}`); `attempt_rocq_proof` parses it
  per `.v`. (Cheaper than a sidecar file; keeps the exit-code contract.)

### B. Feature supervisor (`src/pycsl/agents/feature_supervisor/report.py` + entry)
- New `config/schemas/feature-run-summary.schema.json`.
- New `write_feature_run_summary(...)` → `metrics/feature-supervisor/<slug>/run-summary.json`,
  built from the SAME per-phase outcome data that already feeds `halt-report.md`
  (phase#, level, role, outcome ∈ {STATUS_VERIFIED, PASS, FAIL, CLAIM_REJECTED,
  MISSING_ACCEPTANCE, load-bearing-halt, gate-fail, delegation-fail}; acceptance
  passed/total; gate per-step pass/skip/fail; delegation attempted/succeeded/rolled_back;
  load-bearing hits; per-stub `#@ proof rocq` count + 0-`\trusted` check). Emit on every
  invocation (success and halt), so each 16-steps run appends one datapoint.

## Part 2 — Ingest (`bin/cmmi-metrics-ingest.py`)
- Read `metrics/run-summary/*.json` and `metrics/feature-supervisor/*/run-summary.json`
  and roll the catalog KPIs into `metrics-store.json` (global + per-system), alongside
  the existing `coordinator_retries_week`/`pycsl_proof_pass_rate_week`. New global/per-
  system fields: `fault_correctness{by_class,overall}`, `redecompose_rate`,
  `loop_detect_rate`, `rocq_completion_rate`, `rocq_retries{avg,max}`, `rocq_abort_rate`,
  `delegation{iterations_avg,rollback_rate,gate_passrate,acceptance_passrate,
  status_forged_rate,loadbearing_halt_rate}`, `ncr{count,open_max_age_days}`.
- Keep the existing `source_uri` discipline (reference, don't duplicate).

## Part 3 — Catalog doc (reuse existing skills)
- New `config/skills/cmmi-metrics-collection/references/agent-loop-kpis.md` = the catalog
  above (formulas, sources, axis, QPPO method, the proxy caveat, L4/L5 boundary).
- Extend the **Profile-P** KPI bullet in `cmmi-metrics-collection/SKILL.md` and the
  Phase-1 priority-charts list in `cmmi-quantitative-mgmt/SKILL.md §6` to cite it (so
  the deferred-charts pipeline picks these up at ≥8 snapshots).

## Critical files
- `src/pycsl/agents/coordinator.py` — per-attempt records + `write_run_summary` + Rocq accounting.
- `src/pycsl/agents/agent-rocq-proof-writer.py` — emit retries/status marker.
- `src/pycsl/agents/feature_supervisor/report.py` (+ entry call site) — `write_feature_run_summary`.
- `config/schemas/{run-summary,feature-run-summary}.schema.json` — NEW.
- `bin/cmmi-metrics-ingest.py` — ingest both summaries into `metrics-store.json`.
- `config/skills/cmmi-metrics-collection/references/agent-loop-kpis.md` — NEW catalog; cited from both L4 skills.

## Verification
- New schemas are valid JSON and the summaries validate against them.
- **Axis A:** a forced-failure corpus fixture through `coordinator.py` yields
  `metrics/run-summary/<f>.json` with a populated fault→outcome linkage, redecompose
  count, and Rocq accounting; exit-72/73 paths each emit a summary + NCR.
- **Axis B:** the real `16-steps-exec.md` supervisor run yields
  `metrics/feature-supervisor/16-steps-exec/run-summary.json` with per-phase
  acceptance/gate/delegation/Rocq-citation data (the seed datapoint).
- `bin/cmmi-metrics-ingest.py --show` lists the new KPIs in `metrics-store.json`.
- New tests under `test-suite/agent-tests/`: `test_run_summary.py` (coordinator
  summary + proxy linkage), `test_feature_run_summary.py`, and an ingest test;
  agent suite stays green.
- `CMMI_AUDIT_NESTED=1 bin/cmmi-audit.sh` stays 9/0; doc-coherency unaffected.
- Charts are **deferred** by design: note that SPC/QPPO control limits appear only
  after `--weekly` reaches ≥8 snapshots (existing Profile-P gate) — until then,
  record-only.

## Out of scope
- **L5 CAR** (root-cause analysis of *why* a KPI drifts, and process changes).
- Arbitrary numeric targets before a μ/σ baseline exists.
- The labeled-audit calibration of the reconciliation proxy (future).
