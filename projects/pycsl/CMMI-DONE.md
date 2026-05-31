# CMMI Rollout — Done

**Status:** Operationally complete
**Effective date:** 2026-05-31
**Last reviewed:** 2026-05-31
**Profile:** P (single-developer CCB; per `PROJECT.md`)
**Cumulative plans landed:** `cmmi-tailoring-plan.md` +
`cmmi-tailoring-plan-follow-up.md` +
`cmmi-tailoring-plan-follow-up-2.md` +
`cmmi-tailoring-plan-follow-up-3.md`

---

## What "done" means

The CMMI framework for PyCSL is in place. The user owns running it.

### Concrete deliverables

| Layer | Asset | Verifier |
|---|---|---|
| Scaffold | `projects/pycsl/BL/` + 9 systems × {req, spec, tests, agents, PlantUML} | `bin/cmmi-audit.sh` C8.1+2 / C8.3 / C8.4 / C8.5 |
| BL plan binding | `BL/specifications/main.md` includes `config/skills/csl-from-scratch/SKILL.md` (Squeeze Strategy S1–S9) | C8.3 |
| Squeeze ownership | `PROJECT.md` `squeeze_owners:` (S1→SY3+SY6, S2→SY1, …) | C8.5 |
| Skills tailored | 10 CMMI skills with Profile-P rows in §6 | manual review |
| Tools | 11 `bin/cmmi-*` + `bin/agent-feature-supervisor` | `bin/cmmi-audit.sh` |
| Audit gate | 8 steps: C8.1+2, C8.3, C8.4, C8.5, `[QPM]`, `[BRIDGE]`, `[REG]`, `[lang]` | `bin/cmmi-audit.sh` exit 0 |
| Regression suite | 27 tests under `test-suite/cmmi-regression/` (4 itertools.cycle + 10 queue_reader + 10 supervisor_llm_delegation + 5 supervisor_reader_switch) | `pytest test-suite/cmmi-regression/` |
| Anchor incident regression | `test_itertools_cycle_detection.py` 4 tests against the 2026-05-31 13:47:22 fixture | `[REG]` step |

### What "done" does NOT mean

The framework is in place. The *engineering work* under the
framework is open-ended:

- All squeezes (S1–S9) at 100% strength
- All systems at Profile L individually
- Self-annotation suite covering all of `src/pycsl/`
- Dual-prover cross-check with zero unreconciled pairs
- Stdlib stubs at 100% L4+ coverage

These are long-arc engineering objectives — measured weekly by the
QPM tool, escalated by the Reconciliator (`agent-feature-supervisor`),
proposed by the gap detector (`agent-stdlib-annotate --propose-feature`).
They are **not** gated by the framework rollout.

---

## Steady-state operations

### Daily

| Trigger | Action | Tool |
|---|---|---|
| 05:00 cron | Bridge mirrors recent log activity into the queue | `bin/cmmi-bridge-daily.sh` |
| Per commit (optional) | Composite audit | `bin/cmmi-audit.sh` |

### Weekly

| Trigger | Action | Tool |
|---|---|---|
| Mon 06:00 cron | KPI snapshot appended to `metrics-store.json` | `bin/cmmi-weekly-snapshot.sh` |
| After snapshot | QPM report emitted (auto) | `bin/cmmi-qpm-charts.py` |
| Manually as needed | Gap detection run on stdlib stubs | `bin/agent-stdlib-annotate --detect-gaps` |

### Per-feature

| Trigger | Action | Tool |
|---|---|---|
| Gap category passes threshold (≥5) | Draft `missing-<category>-feature.md` into `proposed-features/` | `bin/agent-stdlib-annotate --propose-feature <cat>` |
| Human reviews, edits, moves to repo root + flips STATUS: APPROVED | Supervised rollout | `bin/agent-feature-supervisor --feature-file <path>` |
| Optionally enable LLM delegation per-feature | Coding LLM produces unified diffs, gate runs, per-phase rollback on failure | add `--allow-llm-delegation` |

### Calendar-gated (one-time events)

| Earliest | Trigger | Action | Effort |
|---|---|---|---|
| 2026-06-14 | ≥14 daily bridge runs + ≥1 supervised 1.4 delegation | Item 3.4r: delete metrics/logs/ fallback from `_read_agent_log_context` | 1-line edit |
| 2026-07-26 | snapshot 8 of 8 arrives | Item 4.AUTO: band auto-flips weak→preliminary; milestone marker emitted (no code change) | 0 |
| After ≥30 days of `bin/cmmi-queue-coverage-diff.py --summary` reporting ≥99.5% coverage with 0 mismatches | Item 3.5x: decommission `coordinator.py` writes (queue becomes primary; `metrics/logs/` becomes derived view) | requires **explicit user authorisation** — separate work item |

---

## When to look at what

The framework is mostly silent. These are the artefacts the user
watches:

| Artefact | When it appears | What it means |
|---|---|---|
| `bin/cmmi-audit.sh` exits non-zero | a gate broke | inspect the failing step, fix, re-run |
| `projects/pycsl/docs/audits/qpm-signal-NNN.md` | a Western Electric rule fired | review the signal, decide whether to investigate the KPI drift |
| `projects/pycsl/docs/audits/qpm-milestone-NNN.md` | a band transition happened (weak→preliminary at snapshot 8; preliminary→stable at snapshot 20) | baselines are now meaningful at a new tier |
| `proposed-features/missing-*-feature.md` with `STATUS: DRAFT` | gap detector found ≥5 stuck functions in a category | review the draft, fill in design options, flip to `APPROVED`, run supervisor |
| `metrics/feature-supervisor/<slug>/halt-report.md` | supervisor halted | read why — load-bearing files, gate failure, or LLM refusal |
| `[BRIDGE]` coverage in `bin/cmmi-audit.sh` drops below 99% | bridge cursor corruption or coordinator write-path change | re-run `bin/cmmi-msg-bridge.py --rebuild`; investigate |

---

## Anti-patterns to avoid

- **Editing `projects/pycsl/BL/.../specifications/main.md` of an L4
  Module index by hand.** They are auto-generated by
  `bin/cmmi-mod-index.py`; hand-edits are wiped on regeneration.
- **Adding a 10th system without updating `PROJECT.md` `squeeze_owners:`
  and the audit `[C8.5]` step.** The audit catches this — coverage
  check fails with "Systems with no Squeeze".
- **Removing entries from the load-bearing deny-list** (`config/skills/
  agent-stdlib-annotate/references/load-bearing-files.md`). Each
  entry is there for a soundness reason; removal requires a
  CCB-tracked commit.
- **Running `bin/agent-feature-supervisor --skip-gate` in CI.**
  That mode is for human smoke-testing only.
- **Disabling the daily bridge cron.** The 14-day clock for Item
  3.4r doesn't tick if the bridge doesn't run; subsequent
  authorisation gates depend on this clock.
- **Decommissioning `coordinator.py` writes (Item 3.5x) without
  ≥30 days of ≥99.5% coverage.** The dual-write phase is the safe
  steady state per `should-we-cmmi-or-not.md` §8 risk 3.
- **Manually appending to `metrics-store.json`.** Snapshots are
  generated by `bin/cmmi-metrics-ingest.py --weekly` only.
  Hand-edits skew control limits.
- **Treating L3-ceiling notes as bugs.** They are *signals* — the
  annotator correctly recognised an expressivity gap. The
  Reconciliator's job is to aggregate them into feature proposals,
  not to "fix" them per stub.

---

## What comes after

There is **no follow-up #4** for the framework itself. Future work
splits cleanly into three buckets:

1. **Operational maintenance** — running the cadence above;
   reacting to gate failures, signals, and milestones. No new plan
   needed.

2. **Feature-driven engineering** — `missing-*-feature.md` plans
   drafted by `--propose-feature` or by the human; supervisor
   orchestrates the rollout. Each feature plan is its own
   deliverable. Examples:
    - `missing-iter-feature.md` (already authored; not yet
      executed)
    - future: `missing-regex-feature.md`, `missing-higher-order-feature.md`,
      etc. — generated automatically when categories cross the
      threshold

3. **Squeeze strengthening** — improving S1–S9 individually:
    - more reference tests for S3
    - more cross-prover reconciliations for S5
    - more self-annotated modules for S4 (currently `errors.py`
      only; growth criteria in `pycsl-stdlib-coverage` §9)
    - more stdlib stubs with full contracts for S8

These are engineering work items, not CMMI work items. Track them
under `docs/stdlib-global-plan.md` or per-system plans
(`projects/pycsl/BL/SY<N>-<Name>/`), not under
`cmmi-tailoring-plan-follow-up-*.md`.

---

## How to verify the rollout is still healthy

A single command:

```bash
bin/cmmi-audit.sh && .venv/bin/python3 -m pytest test-suite/cmmi-regression/ -q
```

Expected output:

```
Summary: 8 passed, 0 failed, 0 skipped
27 passed in <1s>
```

If either fails, **stop and inspect.** The CMMI framework's
correctness is itself a CCB-controlled invariant (Profile-P
self-CCB; commit SHA = CR-ID).

---

## References

- [`PROJECT.md`](PROJECT.md) — the project charter (profile, CCB,
  9-system inventory, squeeze ownership, cron schedules).
- [`BL/specifications/main.md`](BL/specifications/main.md) — the BL
  plan include + Squeeze → System decomposition.
- [`../../config/skills/csl-from-scratch/SKILL.md`](../../config/skills/csl-from-scratch/SKILL.md)
  — the BL plan itself (operational playbook).
- [`../../cmmi-tailoring-plan.md`](../../cmmi-tailoring-plan.md) and
  the three follow-up plans — the change history.
- [`../../should-we-cmmi-or-not.md`](../../should-we-cmmi-or-not.md)
  — the recommendation envelope that started this whole series.
- [`../../better-agent.md`](../../better-agent.md) — the canonical
  Reconciliator design (now ~80% landed in code).
- [`../../missing-iter-feature.md`](../../missing-iter-feature.md)
  — the canonical human-authored feature plan; the regression-test
  anchor.
- `bin/cmmi-audit.sh` — the one-command health check.
