# CMMI Tailoring Plan — Follow-Up #3

## Context

Three follow-up plans have landed in succession:

| Plan | Verdict |
|---|---|
| [`cmmi-tailoring-plan.md`](cmmi-tailoring-plan.md) | Scaffold + 5 `bin/cmmi-*` tools + 10 tailored skills + 6/6 audit gates green |
| [`cmmi-tailoring-plan-follow-up.md`](cmmi-tailoring-plan-follow-up.md) | Items 1.1/1.2/1.3/2/4.1A — supervisor gate-only, gap detection, proposal generation, regression test, weekly snapshot |
| [`cmmi-tailoring-plan-follow-up-2.md`](cmmi-tailoring-plan-follow-up-2.md) | Items 3.1/3.2/3.3 (queue + reader + tests), 4.1B/4.1C/4.AUD (QPM charts + WE rules + audit step), 1.4a/1.4b/1.4c (LLM delegation with rollback) |

Each plan reduced the deferral surface. The remaining 3 items look
*genuinely* gated:

1. **Item 3.4** — supervisor reader switch from `metrics/logs/` to
   the queue. 5-min edit. Gated on ≥14 days of bridge runs
   (earliest 2026-06-14).
2. **Item 3.5** — `coordinator.py` write-path decommission.
   Requires **explicit user authorisation**; dual-write may be
   the right end state.
3. **Item 4.AUTO** — strong-signal QPM mode flip.
   Auto-triggers at snapshot 8 (~2026-07-26). **Zero code change**
   required.

This plan does what the previous two did: turn "gated on X" into
"buildable today with X as the operational signal that flips a
flag." The actual deferrals are decisions, not code.

It also draws the line: what makes CMMI rollout *done*, and what
steady-state operations look like after this plan lands.

---

## Dependency graph

```
Now (today, ~3 hours):
  ┌──────────────────────────────────────────────────────────────────┐
  │ [3.4]   Pre-stage the reader switch:                             │
  │         add _read_agent_log_context(agent, since) to supervisor  │
  │         that uses queue_reader.iter_messages() and falls back to │
  │         metrics/logs/ on empty queue. Backwards-compatible.      │
  │                                                                  │
  │ [3.4t]  Add unit test asserting queue-first / log-fallback order │
  │                                                                  │
  │ [3.5p]  Build bin/cmmi-queue-coverage-diff.py: compares queue    │
  │         contents against metrics/logs/ source-of-truth to        │
  │         quantify bridge fidelity. (Pre-decommission validator.)  │
  │                                                                  │
  │ [4.AT]  Add band-transition detector to cmmi-qpm-charts.py:      │
  │         when the band changes between two consecutive runs       │
  │         (weak→preliminary→stable), emit a milestone marker into  │
  │         projects/pycsl/docs/audits/qpm-milestone-NNN.md.         │
  │                                                                  │
  │ [4.AUDc] Extend [QPM] step in bin/cmmi-audit.sh to print         │
  │          "snapshot K of 8 for preliminary" countdown.            │
  │                                                                  │
  │ [DONE]  Write projects/pycsl/CMMI-DONE.md — declares the         │
  │         rollout complete, defines steady-state operations.       │
  └──────────────────────────────────────────────────────────────────┘
                                       │
                                       │ (≥14 days of clean bridge runs
                                       │  AND ≥1 APPROVED feature plan
                                       │  driven through 1.4 delegation)
                                       ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │ [3.4r]  Remove the metrics/logs/ fallback from                   │
  │         _read_agent_log_context. Single one-line edit.           │
  │         Queue becomes the canonical source.                      │
  └──────────────────────────────────────────────────────────────────┘
                                       │
                                       │ (≥30 days of [3.4r] in place
                                       │  AND user authorisation)
                                       ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │ [3.5]  Decommission coordinator.py writes to metrics/logs/.      │
  │        Bridge becomes primary writer. metrics/logs/ becomes      │
  │        derived view via bin/cmmi-logs-from-queue.py (NEW).       │
  │        HIGH RISK — only execute on explicit authorisation.       │
  └──────────────────────────────────────────────────────────────────┘
                                       │
                                       │ (snapshot 8 arrives)
                                       ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │ [4.AUTO] No code change. cmmi-qpm-charts.py auto-flips weak →   │
  │          preliminary. Milestone marker written by [4.AT].        │
  └──────────────────────────────────────────────────────────────────┘
```

Total today: **~3 hours of code + tests**. The rest is either
operational signal-watching or a separately-authorised decision.

---

## Item 3.4 — supervisor reader switch

The supervisor in gate-only v1 (and the Phase 1.4 LLM-delegation
code) doesn't read agent logs at all today. The "switch" is
forward-looking infrastructure for any future feature that wants
log context (e.g., the LLM delegation prompt could cite recent
agent activity, the halt-report could quote relevant log lines).

The cleanest implementation is **both at once**: ship the queue
reader as primary and keep `metrics/logs/` as fallback. The 14-day
clock then gates only the *fallback removal*, not the switch.

### 3.4 — pre-stage today (~30 min)

| File | Change |
|---|---|
| `src/pycsl/agents/agent-feature-supervisor.py` | Add `_read_agent_log_context(agent: str, since: Optional[datetime] = None, max_messages: int = 100) -> list[str]`. Behaviour: try `queue_reader.iter_messages(agent, since=since)` first; if it yields nothing AND the bridge hasn't run yet (`projects/pycsl/message-queues/.bridge-cursor.json` absent), fall back to reading `metrics/logs/<agent>.log` directly. Returns the raw `line_text` field from queue messages, or raw log lines from the fallback. **No callers yet** — pure scaffolding for future use. |
| `src/pycsl/agents/agent-feature-supervisor.py` | At module top, add `from queue_reader import iter_messages` (with graceful ImportError handling for the case where the bridge isn't set up in a fresh checkout). |

### 3.4t — companion test today (~30 min)

| File | Change |
|---|---|
| `test-suite/cmmi-regression/test_supervisor_reader_switch.py` (NEW) | 3 tests: (a) queue-first when queue has data; (b) fallback to metrics/logs/ when queue is empty; (c) returns [] when neither source has data for the agent. Picked up automatically by `bin/cmmi-audit.sh [REG]`. |

### 3.4r — gated 1-line edit (after ≥14 days of bridge runs + ≥1 1.4 delegation)

| File | Change |
|---|---|
| `src/pycsl/agents/agent-feature-supervisor.py` | Delete the metrics/logs/ fallback branch from `_read_agent_log_context`. The function becomes a thin wrapper over `queue_reader.iter_messages`. |

**Trigger condition**: 2026-06-14 OR later, AND
`bin/cmmi-audit.sh [QPM]` reports ≥14 daily snapshots in
`projects/pycsl/message-queues/.bridge-cursor.json`'s history, AND
the human-tracked count of "feature plans driven through Item 1.4
delegation" is ≥1.

**This is the only future code change in Item 3.4.** Implementation
is a literal 5-line block deletion.

---

## Item 3.5 — `coordinator.py` write-path decommission

This is the high-risk item. The plan in follow-up #1 was explicit:

> Do not enter Phase 2.3 (decommissioning) without explicit
> authorization. The dual-write phase is the safe steady state.

What we *can* do today is **build the validator** that the
decommission decision needs — so when the user eventually
authorises it, the move is data-driven rather than speculative.

### 3.5p — pre-build the coverage-diff validator (~1.5 hours)

| File | Change |
|---|---|
| `bin/cmmi-queue-coverage-diff.py` (NEW) | Compares queue contents against `metrics/logs/` source. For each `metrics/logs/<file>.log:<lineno>`, asserts that a corresponding queue message exists with the same `source_uri`. Reports: (a) coverage rate (queue messages / log lines, excluding blank lines); (b) any source-URI mismatches; (c) any messages whose `line_text` doesn't match the source line. Exits 0 if coverage ≥99% AND zero content mismatches, else 1. |
| `bin/cmmi-queue-coverage-diff.py` | Two modes: `--summary` (just the coverage number) and `--detail` (per-file breakdown). |

The decommission decision is gated on: this tool reporting **≥99.5% coverage with zero content mismatches for 30 consecutive daily runs**. That's the operational floor below which decommissioning is unsound.

### 3.5d — wire into `bin/cmmi-audit.sh` as informational (~15 min)

| File | Change |
|---|---|
| `bin/cmmi-audit.sh` | Add a new `[BRIDGE]` step after `[QPM]`. Runs `bin/cmmi-queue-coverage-diff.py --summary`. Exits OK regardless of result (informational); the printed coverage number is what the user watches. |

### 3.5x — execute the decommission (separate authorisation, not in this plan)

When/if authorisation comes, the changes are:

| File | Change |
|---|---|
| `src/pycsl/agents/coordinator.py` | Remove `metrics/logs/<agent>.log` write calls from the retry loop. Replace with direct queue writes via a new `queue_writer.py` companion to `queue_reader.py`. |
| `src/pycsl/agents/queue_writer.py` (NEW) | Symmetric to `queue_reader.py`. Public API: `emit_message(agent: str, line_text: str, source_uri: Optional[str] = None) -> str` returns the uid. |
| `bin/cmmi-logs-from-queue.py` (NEW) | Reverse mirror — generates `metrics/logs/<agent>.log` from the queue for backward-compat with humans grepping logs. |
| `bin/cmmi-msg-bridge.py` | Migrates from "log-source bridge" to "primary writer". |

**Risk profile**: `coordinator.py` is the central agent orchestrator
across the whole project. Breaking its observability surface
breaks the entire LLM-agent pipeline. The 99.5%/30-day gate is
intentionally conservative.

---

## Item 4.AUTO — strong-signal QPM mode flip

Zero code change required at week 8 — `bin/cmmi-qpm-charts.py`
already auto-flips. What we *can* add today is **detection and
visibility**: a milestone marker + countdown in the audit.

### 4.AT — band-transition detector (~30 min)

| File | Change |
|---|---|
| `bin/cmmi-qpm-charts.py` | At the top of `main()` (default emit mode), compare the band of `snapshots[-2]` vs `snapshots[-1]` (when both exist). If the band changed (weak → preliminary, or preliminary → stable), write `projects/pycsl/docs/audits/qpm-milestone-NNN.md` with: previous band, new band, snapshot count, KPI summary, link to the just-written report. Idempotent — checks for an existing milestone with the same band-transition tag before writing. |

The milestone marker is auditable evidence that QPM crossed a
phase boundary. Useful for:
- Knowing when to start trusting the control-chart limits.
- Triggering downstream actions (e.g., decide whether to publish
  baselines to a wider audience).
- Documenting the long-arc progression for external reviewers.

### 4.AUDc — countdown in `[QPM]` audit step (~15 min)

| File | Change |
|---|---|
| `bin/cmmi-audit.sh` | Update `[QPM]` block to also print a one-line countdown: `snapshots K of 8 for preliminary mode (~D days at weekly cadence)`. Trivial arithmetic on the current snapshot count. |
| `bin/cmmi-qpm-charts.py` `--check` mode | Print the countdown line in the same format so the audit step doesn't have to duplicate the logic. |

---

## CMMI rollout — Definition of Done

This plan completes the rollout. After it lands, the framework is
operationally complete. The user owns running it.

### What "done" means

| Layer | Status after this plan |
|---|---|
| **Scaffold** (`projects/pycsl/BL/`, agent personas, PlantUML stubs) | Complete — built by `cmmi-tailoring-plan.md` Phase A |
| **Tools** (`bin/cmmi-*`) | Complete — 7 tools total: `audit`, `bridge-daily`, `include-expand`, `metrics-ingest`, `mod-index`, `msg-bridge`, `qpm-charts`, `queue-coverage-diff`, `weekly-snapshot`. Plus `agent-feature-supervisor` wrapper. |
| **Skills** (10 tailored with Profile-P) | Complete — every CMMI skill has a Profile-P deviation row |
| **Audit gate** (`bin/cmmi-audit.sh`) | Complete — 7 steps + new `[BRIDGE]` informational = 8 |
| **Regression suite** (`test-suite/cmmi-regression/`) | Complete — 24 tests + 3 new in this plan = **27** |
| **Anchor incident regression** | Covered — `test_itertools_cycle_detection.py` 4 tests |
| **Per-system spec mirror** | Complete — 9 systems × {req, spec, tests, agents, PlantUML} |
| **L4 indices** | Auto-generated, currently 3,553 defs across 252 files |
| **Trust chain** (S1–S9 squeeze ownership) | Documented in `PROJECT.md` + enforced by C8.5 |

### What "done" does NOT mean

CMMI rollout = the framework is in place. It does NOT mean:

- All squeezes (S1–S9) are at 100% strength.
- All systems are at Profile L individually.
- The self-annotation suite covers all of `src/pycsl/`.
- The dual-prover cross-check has zero unreconciled pairs.

Those are *long-arc* engineering objectives — measured weekly by
the QPM tool, not gated by the rollout. The CMMI framework
provides the *measurement and escalation infrastructure*; the
underlying engineering work proceeds independently.

### Steady-state operations

After this plan lands, the daily/weekly/quarterly operations are:

| Cadence | Action | Tool |
|---|---|---|
| Daily | Bridge runs at 05:00 (cron) | `bin/cmmi-bridge-daily.sh` |
| Daily | Audit runs as part of regular CI (or local before commit) | `bin/cmmi-audit.sh` |
| Weekly (Mon 06:00) | Snapshot accumulates | `bin/cmmi-weekly-snapshot.sh` |
| Per commit | Doc-coherency + audit | `bin/cmmi-audit.sh` |
| Per `--detect-gaps` run | Gap report updated | `bin/agent-stdlib-annotate --detect-gaps` |
| Per approved `missing-*-feature.md` | Supervised rollout | `bin/agent-feature-supervisor --feature-file <path>` |
| At snapshot 8 (~2026-07-26) | Band auto-flips weak → preliminary; milestone emitted | none (automatic) |
| At ≥14 daily bridge runs + ≥1 1.4 delegation | Item 3.4r reader-switch finalisation | 5-line block deletion |
| At ≥30 days of ≥99.5% bridge coverage + authorisation | Item 3.5 decommission | separate work item |

### Triggers (when to look)

- **`bin/cmmi-audit.sh` exits non-zero**: a gate broke. Inspect the
  failing step's output, fix, re-run. This is the only "must act
  now" signal.
- **`projects/pycsl/docs/audits/qpm-signal-*.md` appears**: a
  Western Electric rule fired. Read the signal, decide whether to
  investigate the KPI drift (no auto-action — informational).
- **`projects/pycsl/docs/audits/qpm-milestone-*.md` appears**: a
  band-transition happened. Celebrate / decide what to do with
  the newly-stable baselines.
- **`proposed-features/missing-*-feature.md` appears with
  `STATUS: DRAFT`**: the gap detector found enough stuck functions
  in a category. Review the draft, fill in the design options, flip
  to `APPROVED`, run the supervisor.

---

## Critical files (across all 3 items)

**New (3 files):**
- `bin/cmmi-queue-coverage-diff.py` (3.5p)
- `test-suite/cmmi-regression/test_supervisor_reader_switch.py` (3.4t)
- `projects/pycsl/CMMI-DONE.md` — declaration of completion + steady-state ops

**Modified (3 files):**
- `src/pycsl/agents/agent-feature-supervisor.py` — add
  `_read_agent_log_context` (3.4)
- `bin/cmmi-qpm-charts.py` — band-transition detector + countdown
  line (4.AT + 4.AUDc helper)
- `bin/cmmi-audit.sh` — `[BRIDGE]` step + updated `[QPM]`
  countdown line (3.5d + 4.AUDc)

**Not modified (left for the authorisation event):**
- `src/pycsl/agents/coordinator.py` — Item 3.5x
- `bin/cmmi-msg-bridge.py` — Item 3.5x migration
- New: `src/pycsl/agents/queue_writer.py`, `bin/cmmi-logs-from-queue.py` — Item 3.5x

---

## Execution order

```
Today (~3 hours):
  1. [3.4]   Add _read_agent_log_context to supervisor             30 min
  2. [3.4t]  test_supervisor_reader_switch.py                      30 min
  3. [3.5p]  Build bin/cmmi-queue-coverage-diff.py                 1.5 hours
  4. [3.5d]  Wire [BRIDGE] step into bin/cmmi-audit.sh             15 min
  5. [4.AT]  Band-transition detector in cmmi-qpm-charts.py        30 min
  6. [4.AUDc] Countdown line in [QPM] step                         15 min
  7. [DONE]  Write projects/pycsl/CMMI-DONE.md                     30 min

Calendar-gated (no code in this plan):
  ≥14 daily bridge runs + ≥1 1.4 delegation (~2026-06-14):
     [3.4r] Delete metrics/logs/ fallback (5-line edit)

  snapshot 8 (~2026-07-26):
     [4.AUTO] Automatic — milestone marker emitted by [4.AT]

  ≥30 days of ≥99.5% bridge coverage + USER AUTHORISATION:
     [3.5x] Execute decommission — separate work item
```

Total code today: **~3 hours**. Everything else is
operational signal-watching.

---

## Verification

After all today's items land:

| Gate | Expected output |
|---|---|
| `bin/cmmi-audit.sh` | 8 passed (`C8.1+2`, `C8.3`, `C8.4`, `C8.5`, `[QPM]` with countdown, `[BRIDGE]` coverage %, `[REG]` with 27 tests, `[lang]`) |
| `pytest test-suite/cmmi-regression/` | 27 passed |
| `bin/cmmi-queue-coverage-diff.py --summary` | reports current coverage (likely high — bridge already mirrored everything) |
| `bin/cmmi-qpm-charts.py` | report unchanged; `--check` now prints `snapshots K of 8 for preliminary mode (~(8-K)*7 days)` |
| `cat projects/pycsl/CMMI-DONE.md` | declares completion + lists steady-state operations |

**Per-item acceptance:**

| Item | Acceptance command | Expected |
|---|---|---|
| 3.4 | `python3 -c "from agent_feature_supervisor import _read_agent_log_context as r; print(len(r('agent-stdlib-annotate', max_messages=3)))"` (after dynamic import) | returns a list — queue-first, log-fallback |
| 3.4t | `pytest test-suite/cmmi-regression/test_supervisor_reader_switch.py -v` | 3/3 PASS |
| 3.5p | `bin/cmmi-queue-coverage-diff.py --summary` | reports coverage % vs metrics/logs/ |
| 3.5d | `bin/cmmi-audit.sh` includes `[BRIDGE]` informational line | one new step visible |
| 4.AT | (manually backdate `snapshots[]` to simulate a transition) run `bin/cmmi-qpm-charts.py` → check `projects/pycsl/docs/audits/qpm-milestone-001.md` exists | milestone marker emitted |
| 4.AUDc | `bin/cmmi-audit.sh [QPM]` block | shows `snapshots K of 8 for preliminary mode (~D days)` line |

---

## Risks specific to this plan

- **3.4 fallback hides bridge breakage.** If the queue silently
  fails (e.g., cursor corruption causes empty inboxes), the
  fallback to `metrics/logs/` masks it. **Mitigation**:
  `bin/cmmi-audit.sh [BRIDGE]` step makes this visible — coverage
  drops to 0% if the bridge cursor is broken.
- **3.5p coverage check on 81k messages is slow.** Reading every
  queue JSON + cross-referencing every log line could take
  seconds-to-minutes. **Mitigation**: `--summary` mode samples
  (default 5%); `--detail` mode walks everything. Audit step
  uses `--summary`.
- **4.AT writes spurious milestone markers if user does
  `bin/cmmi-qpm-charts.py` multiple times.** **Mitigation**:
  detector checks for an existing milestone with the same
  `(prev_band, new_band, snapshot_count)` tag before writing.
- **3.4r removal forgotten.** The fallback could live indefinitely
  if no one watches the calendar. **Mitigation**: `[BRIDGE]` step
  prints a "fallback still active — consider 3.4r" warning when
  coverage > 99% and ≥14 daily bridge runs have happened.
- **3.5x triggered prematurely.** A user excited about the 99.5%
  coverage metric might decommission too early. **Mitigation**:
  the plan explicitly requires authorisation; no automation
  initiates 3.5x.
- **CMMI-DONE.md becomes stale.** As steady-state operations
  evolve, the doc rots. **Mitigation**: doc has a "Last reviewed"
  timestamp; coherency audit could check it's been touched in
  the last 6 months (not implemented in this plan — possible
  follow-up).

---

## What this plan does NOT do

- Does not execute Item 3.5x (`coordinator.py` decommission).
  Permanent stand-still until explicit authorisation.
- Does not delete the `metrics/logs/` fallback in `_read_agent_log_context`.
  That's Item 3.4r, gated on the 14-day clock.
- Does not predict band transitions. The milestone detector reacts
  to transitions; it doesn't forecast them.
- Does not auto-publish QPM reports to anything external (no
  email/Slack/dashboard wiring). Reports go to disk; the user
  views them.
- Does not modify Profile-P or the 9-system topology. The
  framework is settled.
- Does not introduce a 4th tailoring profile. Profile-P is the
  end state for PyCSL.
- Does not retrofit the 8 `pycsl-*` domain skills. Their format
  is correct as-is; coherency is enforced by `bin/doc-coherency.py`.
- Does not commit any change. The user stages and commits
  themselves (single-developer CCB; commit SHA = CR-ID).

---

## What comes AFTER CMMI rollout is done

The follow-up plan series is *not* infinite. After this plan
lands, there is no follow-up #4 for the framework itself. Future
work splits into three buckets:

1. **Operational maintenance** — running the daily/weekly/quarterly
   cadence above; reacting to gate failures, signals, and
   milestones. No new plan needed.

2. **Feature-driven engineering** — the actual PyCSL work
   (extending the contract surface, improving the proof corpus,
   shipping new `missing-*-feature.md` plans). Each feature plan
   is its own deliverable, drafted by `--propose-feature` or by
   the human; the supervisor orchestrates the rollout.

3. **Squeeze strengthening** — improving S1–S9 individually
   (more reference tests for S3, more cross-prover reconciliations
   for S5, more self-annotation modules for S4, etc.). These are
   engineering work-items, not CMMI work-items. They get tracked
   under `docs/stdlib-global-plan.md` or per-system plans, not
   under `cmmi-tailoring-plan-follow-up-*.md`.

The CMMI framework provides infrastructure for tracking (3) via
QPM charts and (2) via the Reconciliator. It does not do the
underlying engineering work.

---

## References

- [`cmmi-tailoring-plan.md`](cmmi-tailoring-plan.md) — Profile-P + 9-system topology.
- [`cmmi-tailoring-plan-follow-up.md`](cmmi-tailoring-plan-follow-up.md) — Items 1.1/1.2/1.3/2/4.1A.
- [`cmmi-tailoring-plan-follow-up-2.md`](cmmi-tailoring-plan-follow-up-2.md) — Items 3.1–3.3, 4.1B/4.1C/4.AUD, 1.4a/1.4b/1.4c.
- [`should-we-cmmi-or-not.md`](should-we-cmmi-or-not.md) §8 risk 3 — "two substrates indefinitely is a bug" / Item 3.5 hard rule.
- [`better-agent.md`](better-agent.md) — the canonical supervisor design (now ~70% landed in code).
- [`missing-iter-feature.md`](missing-iter-feature.md) — anchor feature plan; regression-test input.
- `projects/pycsl/PROJECT.md` — single-developer CCB; bridge + snapshot cron entries documented.
- `bin/cmmi-audit.sh` — the composite gate this plan extends to 8 steps.
- `src/pycsl/agents/queue_reader.py` — the substrate `_read_agent_log_context` (Item 3.4) calls.
- `src/pycsl/agents/agent-feature-supervisor.py` — extended one more time by Item 3.4.
- `bin/cmmi-msg-bridge.py` — generates the queue contents that
  `cmmi-queue-coverage-diff.py` (Item 3.5p) validates against
  `metrics/logs/`.
