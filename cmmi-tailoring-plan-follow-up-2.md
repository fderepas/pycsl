# CMMI Tailoring Plan — Follow-Up #2

## Context

[`cmmi-tailoring-plan-follow-up.md`](cmmi-tailoring-plan-follow-up.md)
landed 5 deliverables (Items 1.1, 1.2, 1.3, 2, 4.1A) and explicitly
deferred 3 items because they each have a separate kind of blocker:

1. **Item 3 — `communication` Phase 2 sunset** — needs the supervisor
   (Item 1.3, now done) AND ≥2 weeks of bridge runs in dual-write
   before any reader switches over.
2. **Item 1.4 — coding-LLM delegation** — explicitly optional; the
   gate-only supervisor (v1) covers the 80% case where the human
   wants to drive the edits manually.
3. **Item 4.1B + 4.1C — control charts + Western Electric rule
   detection** — blocked on clock (need ≥8 weekly snapshots; today
   is snapshot #1).

This plan separates **what can be built now** from **what must be
gated on signal or time**, and treats each item that way:

- **Item 3** — build the reader-side path against a synthetic queue
  fixture today; wire the cron entry now so the 2-week dual-write
  window starts now; defer only the cutover decision.
- **Item 1.4** — design the prompt + rollback flow now; ship behind
  a feature flag (`--allow-llm-delegation`) that defaults off; let
  the human enable it per-feature when they want it.
- **Item 4.1B + 4.1C** — build `bin/cmmi-qpm-charts.py` against the
  available snapshots now; emit "weak signal (n=K, need ≥8)" tags
  when `n < 8`; the tool flips automatically to strong-signal
  reporting when enough snapshots accumulate. **No actual code is
  blocked on the clock.**

Starting-state recap (verified by `bin/cmmi-audit.sh` after follow-up #1):

| Asset | Status |
|---|---|
| `bin/cmmi-msg-bridge.py` | Built; `--dry-run` validated (81,702 messages, 119 agents). **Never run for real yet.** |
| `src/pycsl/agents/agent-feature-supervisor.py` | Built (gate-only v1); exits 74/75/76 per convention; halt-reports work. |
| `projects/pycsl/message-queues/` | Empty (no bridge runs yet). |
| `metrics/feature-supervisor/<slug>/halt-report.md` | One halt-report exists (from the `missing-iter-feature.md` smoke test). |
| `projects/pycsl/docs/metrics/metrics-store.json` | 1 snapshot (`latest` + `snapshots[]` with 1 entry). |
| `bin/cmmi-audit.sh` | 6/6 gates pass: C8.1+2, C8.3, C8.4, C8.5, REG, lang. |

---

## Dependency graph

```
Today (no blockers):
  ┌──────────────────────────────────────────────────────────────────┐
  │ [3.1]  Run cmmi-msg-bridge.py daily (start the 2-week clock)     │
  │ [3.2]  Build queue reader as a library (queue_reader.py)         │
  │ [3.3]  Build synthetic-queue fixture + unit tests for [3.2]      │
  │ [1.4a] Design coding-LLM prompt + add --allow-llm-delegation flag│
  │        defaulting off; supervisor halt path is unchanged         │
  │ [1.4b] Build per-phase git-tag + rollback helper                 │
  │ [1.4c] Add end-to-end test exercising a tiny mock LLM            │
  │ [4.1B] Build cmmi-qpm-charts.py with weak/strong-signal modes    │
  │ [4.1C] Add Western Electric rule detection (4 rules)             │
  │ [4.AUD] Wire [QPM] step into bin/cmmi-audit.sh                   │
  └──────────────────────────────────────────────────────────────────┘
                                       │
                                       │ (2 weeks of bridge runs)
                                       ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │ [3.4]  Switch supervisor reader from metrics/logs/ to queue      │
  │        (one-line change; gated on [3.3] tests passing)           │
  └──────────────────────────────────────────────────────────────────┘
                                       │
                                       │ (≥10 supervisor gate runs +
                                       │  ≥1 APPROVED feature plan E2E)
                                       ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │ [3.5]  Authorisation gate for coordinator.py write-path          │
  │        decommission — NOT auto-executed, separate decision       │
  └──────────────────────────────────────────────────────────────────┘
                                       │
                                       │ (8+ weekly snapshots accumulate)
                                       ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │ [4.STRONG] First strong-signal QPM report                        │
  │            (no code change; bin/cmmi-qpm-charts.py auto-flips)   │
  └──────────────────────────────────────────────────────────────────┘
```

Total "buildable today" work: **~8 days**. Total work blocked on
external signals: **2 small touchpoints (3.4 cutover one-liner; 3.5
authorisation)**, none of which require new design.

---

## Item 3 — `communication` Phase 2 sunset (no-cost preparation)

### 3.1 — Start the dual-write window today (30 min)

The 2-week clock that gates Phase 2 cutover only starts ticking
**after the bridge actually runs**. Until then we are postponing
the gate indefinitely. Fix: run the bridge daily, even though the
supervisor isn't reading from the queue yet.

| File | Change |
|---|---|
| `bin/cmmi-bridge-daily.sh` (NEW) | Wrapper around `bin/cmmi-msg-bridge.py` with `flock` and a `--max-age-days 30` arg (added in 3.1a below) to keep volume bounded. Same pattern as `bin/cmmi-weekly-snapshot.sh`. |
| `projects/pycsl/PROJECT.md` | New "Bridge schedule" subsection under "Snapshot schedule" documenting the daily cron entry. |
| `bin/cmmi-msg-bridge.py` (3.1a) | Add `--max-age-days N` arg. Only mirror log lines from files whose `mtime` is within N days. Default 30 (~250 messages/day at observed rate vs. 81k for the all-time backfill). |

**Acceptance criterion (Phase 3.1):**
```bash
bin/cmmi-bridge-daily.sh
ls projects/pycsl/message-queues/ | wc -l
# expected: >= 1 (number of agents with recent log activity)
```

**Cron entry to add (manual, documented in PROJECT.md):**
```cron
0 5 * * * cd ~/git/pycsl && bin/cmmi-bridge-daily.sh >> metrics/cron.log 2>&1
```
Daily at 05:00, one hour before the weekly snapshot.

### 3.2 — Queue reader as a library (1 day)

Extract the queue-reading logic into a reusable library so the
supervisor (and any future consumer) doesn't duplicate it.

| File | Change |
|---|---|
| `src/pycsl/agents/queue_reader.py` (NEW) | Pure-Python module. Public API: `iter_messages(agent: str, since: Optional[datetime] = None) -> Iterator[dict]` walks `projects/pycsl/message-queues/<agent>/inbox-from-logs/*.json` sorted by filename (stable hash, deterministic order); `read_message(uid: str) -> Optional[dict]` looks up by uid; `agents() -> list[str]` enumerates. No state; pure read. |
| `src/pycsl/agents/queue_reader.py` | Validates the JSON `schema` field matches `pycsl-cmmi-bridge-v1` (the schema string the bridge writes). |

This is library code only — no agent script changes yet.

**Acceptance criterion (Phase 3.2):**
```python
from queue_reader import iter_messages
msgs = list(iter_messages("agent-stdlib-annotate"))
assert all(m["schema"] == "pycsl-cmmi-bridge-v1" for m in msgs)
```

### 3.3 — Synthetic-queue fixture + unit tests (1 day)

Test 3.2 against a controlled fixture so we don't depend on real
log content.

| File | Change |
|---|---|
| `test-suite/cmmi-regression/fixtures/queue-fixture-tiny.tar` (NEW) | A tiny tarball containing `projects/pycsl/message-queues/test-agent/inbox-from-logs/<5 msgs>`. Extracted into `tmp_path` by the test. |
| `test-suite/cmmi-regression/test_queue_reader.py` (NEW) | 5 tests: round-trip a synthetic message; iter ordering; missing-schema rejection; agent enumeration; since-filter. |
| `bin/cmmi-audit.sh` | The `[REG]` step's pytest run automatically picks these up. |

**Acceptance criterion (Phase 3.3):** `[REG]` count rises from
4 → 9 tests, all PASS.

### 3.4 — Supervisor reader switch (1 line; gated on [3.3] + 2 weeks)

When Phase 3.1 has been running for ≥14 days AND Phase 3.3 tests
pass, change one method in `agent-feature-supervisor.py` from
reading `metrics/logs/<agent>.log` to calling
`queue_reader.iter_messages(<agent>)`. **The supervisor's gate-only
v1 currently doesn't read logs at all**, so this is forward-looking
infrastructure — the genuine switch comes when Item 1.4
(coding-LLM delegation) lands and the supervisor starts citing log
context in its prompts.

| File | Change |
|---|---|
| `src/pycsl/agents/agent-feature-supervisor.py` | When constructing context for an LLM call (Item 1.4-era), use `queue_reader` instead of opening `metrics/logs/*.log` directly. |

**This step is a 5-line change.** No new tests needed beyond
re-running the regression suite.

### 3.5 — `coordinator.py` write-path decommission (separate authorisation)

**Explicitly NOT in scope of this plan.** Per
`cmmi-tailoring-plan-follow-up.md` Item 3 "Hard rule":

> Do not enter Phase 2.3 (decommissioning) without explicit
> authorization. The dual-write phase (2.1 + 2.2) is the safe
> steady state; we can live there indefinitely.

When/if the user authorises 3.5, the changes are:

| File | Change |
|---|---|
| `src/pycsl/agents/coordinator.py` | Remove `metrics/logs/<agent>.log` writes from the retry loop. **High-risk edit.** |
| `bin/cmmi-logs-from-queue.py` (NEW) | Reverse mirror — generate `metrics/logs/<agent>.log` from the queue for backward compat with humans grepping logs. |
| `bin/cmmi-msg-bridge.py` | Migrate from "log-source bridge" to "primary writer" — accept structured events directly from agents instead of mirroring log lines. |

### Item 3 effort (today)

| Sub-item | Effort | Status |
|---|---|---|
| 3.1 — cron entry + `--max-age-days` | 30 min | shippable today |
| 3.2 — `queue_reader.py` library | 1 day | shippable today |
| 3.3 — synthetic-queue fixture + tests | 1 day | shippable today |
| 3.4 — supervisor reader switch | 5 min (gated) | gated on 2-week dual-write |
| 3.5 — `coordinator.py` decommission | NOT IN SCOPE | requires separate authorisation |

**~2 days of code today. Phase 2 cutover (3.4) automatic
after the clock runs.**

---

## Item 1.4 — coding-LLM delegation

The supervisor never edits load-bearing files (always halts with
exit 75 — that contract is preserved). The new capability:
**for phases whose targets are NOT load-bearing**, delegate the
edit to a coding LLM, apply with `git apply`, run the gate,
rollback on failure.

The natural candidates from `missing-iter-feature.md` are:
- **Phase 3 — Stdlib stub refresh** (`src/pycsl_lib/itertools.py`,
  `src/pycsl_lib/builtins.py`, plus reference-test files under
  `test-suite/corpus/python-reference/stdlib/itertools/`).
- **Phase 4 — Coverage classifier update** (`bin/stdlib-coverage-report.py`,
  `docs/stdlib-global-plan.md`).

Both are mechanical work — stub promotion + classifier extension —
that the existing `agent-stdlib-annotate` already does in
isolation. The supervisor's job is to do them *in the context of an
approved feature plan* and run the gate between phases.

### 1.4a — Design the prompt + flag (1 day)

| File | Change |
|---|---|
| `src/pycsl/agents/agent-feature-supervisor.py` | Add `--allow-llm-delegation` arg (defaults to FALSE — gate-only mode preserved). When TRUE and a phase has no deny-list hits, build a phase-scoped prompt and dispatch via `llm_generate`. |
| `src/pycsl/agents/agent-feature-supervisor.py` | New `_build_phase_prompt(phase: Phase, plan_text: str) -> str` function. The prompt includes: (a) the BL plan reference (`csl-from-scratch` §0.5 mention so the LLM knows the goal); (b) the phase title and full body text from the plan; (c) explicit instructions: *"Output a unified diff (`diff --git a/... b/...`) for the named target files only. Do not edit files not listed in the phase. Do not delete tests. Wrap diff in a fenced code block tagged `diff`."*; (d) the contents of the target files (read & inlined). |
| `config/skills/agent-stdlib-annotate/references/coding-llm-prompt.md` (NEW) | The system-prompt scaffold the supervisor wraps around the per-phase content. ~50 lines covering output format, scope rules, refusal behavior. |

The prompt deliberately constrains the LLM to a unified-diff output
format — easier to validate (`git apply --check`) than free-form
file contents, and trivially rollback-able.

### 1.4b — Per-phase git-tag + rollback helper (1 day)

| File | Change |
|---|---|
| `src/pycsl/agents/agent-feature-supervisor.py` | Before each delegated phase: `git tag feature-<slug>-phase-<N>-start HEAD`. On gate failure: `git restore --source=feature-<slug>-phase-<N>-start --staged --worktree -- <target files>`. Then delete the tag. On success: keep the tag (audit trail). |
| `src/pycsl/agents/agent-feature-supervisor.py` | All git invocations go through a `_git(*args) -> str` wrapper that never accepts user-controlled paths without `--` separator (prevent injection through phase target paths that contain `--`). |
| `src/pycsl/agents/agent-feature-supervisor.py` | NEVER use `git reset --hard` or `git clean -f`. Only `git restore --source=<tag> -- <files>`. |

This is the **rollback policy** from `better-agent.md` §Phase 3
point 4. The git-tag approach gives us:
- Atomic-feeling rollback (no partial state).
- Audit trail (failed-attempt tags stay if the user wants them).
- No history rewrite.

### 1.4c — End-to-end test with mock LLM (1 day)

| File | Change |
|---|---|
| `test-suite/cmmi-regression/test_supervisor_llm_delegation.py` (NEW) | Test that monkey-patches `llm_generate` to return a known unified diff (one-line `+ # comment` against `src/pycsl_lib/itertools.py:cycle`). Asserts: (a) `git apply --check` passes; (b) the diff lands; (c) the gate runs and reports OK; (d) the per-phase tag exists. Companion test for the gate-fail rollback path. |
| `test-suite/cmmi-regression/fixtures/mock-llm-diff.patch` (NEW) | The canonical mock diff payload. |
| `bin/cmmi-audit.sh` `[REG]` step | Auto-picks-up new test. |

### 1.4d — `proposed-features/STATUS: APPROVED` watch (optional, 30 min)

The current supervisor takes `--feature-file <path>` and ignores
`STATUS:`. Add a `--watch-approved` mode that polls
`proposed-features/missing-*-feature.md` and invokes itself on any
file whose first 10 lines contain `STATUS: APPROVED`. **Optional**
— manual invocation works fine for the foreseeable future.

### Item 1.4 effort

| Sub-item | Effort |
|---|---|
| 1.4a — prompt + flag | 1 day |
| 1.4b — git-tag + rollback | 1 day |
| 1.4c — mock-LLM tests | 1 day |
| 1.4d — watch mode (optional) | 30 min |

**~3 days. Ships behind `--allow-llm-delegation` flag (defaults
off), so it doesn't change the supervisor's default behavior.**

### Item 1.4 safety perimeter (unchanged invariants)

These rules hold whether `--allow-llm-delegation` is on or off:

1. Load-bearing deny-list always wins. A phase touching any
   deny-listed file halts with exit 75, regardless of the flag.
2. The verification gate always runs after every phase.
3. `git push`, `git commit`, `git reset --hard`, `git clean -f` are
   NEVER invoked by the supervisor.
4. Staging is the human's job. The supervisor leaves edits in the
   working tree; the human reviews `git diff` before committing.
5. On gate failure, the supervisor reverts the *current phase's*
   edits via the per-phase tag, then halts with exit 74. It does
   NOT re-run, does NOT escalate to other LLMs.

---

## Item 4.1B + 4.1C — control charts + Western Electric rules

The plan's text marked these "blocked on clock". On reflection,
only the *strong-signal output* is blocked. The *tool* can be
built now and run against the 1 available snapshot — it just
reports "weak signal (n=K, need ≥8 for strong)".

### 4.1B — `bin/cmmi-qpm-charts.py` (2 days)

| File | Change |
|---|---|
| `bin/cmmi-qpm-charts.py` (NEW) | Read `projects/pycsl/docs/metrics/metrics-store.json`. For each KPI in the 4-chart set, extract the time series across `snapshots[]`. Compute μ + σ + UCL (μ+3σ) + LCL (max(0, μ−3σ)). Emit a Markdown table per KPI per system, optionally a matplotlib chart (PNG to `projects/pycsl/docs/diagrams/qpm-<KPI>-<system>.png`) when matplotlib is importable, otherwise an ASCII spark-line. Output to `projects/pycsl/docs/reports/qpm-report-<NNN>.md`. |
| `bin/cmmi-qpm-charts.py` | When `len(snapshots) < 8`: print "weak signal (n=K)" tag at the top of each chart; do not compute control limits. When `8 ≤ n < 20`: print "preliminary" tag; compute limits with warning. When `n >= 20`: print "stable" tag. |

The 4 KPIs:

| Chart | Per-system metric | Source |
|---|---|---|
| Proof-success rate trend | `pycsl --proof` PASS / total | `metrics-store.json` `systems[i].pycsl_proof_pass_rate` (NEW field — add in 4.1B prep step) |
| Agent retry-count drift | `coordinator.py` retry count per run | `metrics-store.json` `global.coordinator_retries_avg` (NEW field) |
| L3-ceiling rate trend per system | `# cite:_note:` markers per system | `metrics-store.json` `systems[i].l3_ceiling_notes` (already collected) |
| Doc-coherency events / week | `bin/doc-coherency.py` exits | `metrics-store.json` `global.doc_coherency_events_week` (NEW field) |

### 4.1B prep — extend `cmmi-metrics-ingest.py` (½ day)

Two of the four KPIs need additional ingest:

| File | Change |
|---|---|
| `bin/cmmi-metrics-ingest.py` | Add `_collect_pycsl_proof_pass_rate(sy_id, src_root) -> float`: parses recent `metrics/logs/*.log` lines matching `pycsl --proof` outcomes, computes ratio over the last 7 days. Add `_collect_coordinator_retries(...)` similarly. Add `_count_doc_coherency_events_last_week()`. Wire all 3 into `collect_system` / `collect_global`. |

The data accumulates from snapshot #2 onwards. Snapshot #1 (today)
reports `None` for the new fields, which 4.1B handles gracefully.

### 4.1C — Western Electric rule detection (1 day, after 4.1B)

| File | Change |
|---|---|
| `bin/cmmi-qpm-charts.py` | Add `_detect_signals(series: list[float], mu: float, sigma: float) -> list[dict]`. Apply the 4 standard WE rules: (1) 1 point beyond ±3σ; (2) 2 of 3 consecutive points beyond ±2σ on same side; (3) 4 of 5 consecutive points beyond ±1σ on same side; (4) 8 consecutive points on same side of μ. Emit a "Signals" section to the QPM report listing rule hits with the offending snapshot indices. |
| `bin/cmmi-audit.sh` | `[QPM]` step (4.AUD below) escalates rule hits as Workflow-3 events: write `projects/pycsl/docs/audits/qpm-signal-<NNN>.md` per hit. Audit step exit is non-blocking (informational only) since SPC signals are aids, not blockers. |

### 4.AUD — wire `[QPM]` into `bin/cmmi-audit.sh` (½ day)

| File | Change |
|---|---|
| `bin/cmmi-audit.sh` | New `[QPM]` step after `[REG]`. Runs `bin/cmmi-qpm-charts.py --check`. Reports: current snapshot count, signal status (weak/preliminary/stable), any WE rule violations. Always passes (`skip` semantics) when in weak-signal mode, since there's nothing to verify yet. |
| `bin/cmmi-qpm-charts.py` | Add `--check` mode that exits 0 always (informational); separate from default mode which emits the report. |
| `bin/cmmi-audit.sh` | Stale-snapshot check: if newest snapshot is >10 days old, print warning. |

### 4.AUTO — automatic strong-signal flip (no work)

When `metrics-store.json` accumulates ≥8 snapshots,
`bin/cmmi-qpm-charts.py` automatically switches from "weak" to
"preliminary" mode. No code change required at week 8.

### Item 4 effort

| Sub-item | Effort | When |
|---|---|---|
| 4.1B prep — extend `cmmi-metrics-ingest.py` | ½ day | today |
| 4.1B — `cmmi-qpm-charts.py` core | 2 days | today |
| 4.1C — WE rule detection | 1 day | after 4.1B |
| 4.AUD — `[QPM]` step | ½ day | today |
| 4.AUTO — strong-signal flip | 0 (automatic) | week 8 |

**~4 days, all buildable today. First strong-signal report
arrives automatically at week 8.**

---

## Critical files (across all 3 items)

**New (10 files):**
- `bin/cmmi-bridge-daily.sh` (3.1)
- `bin/cmmi-qpm-charts.py` (4.1B + 4.1C)
- `src/pycsl/agents/queue_reader.py` (3.2)
- `config/skills/agent-stdlib-annotate/references/coding-llm-prompt.md` (1.4a)
- `test-suite/cmmi-regression/fixtures/queue-fixture-tiny.tar` (3.3)
- `test-suite/cmmi-regression/fixtures/mock-llm-diff.patch` (1.4c)
- `test-suite/cmmi-regression/test_queue_reader.py` (3.3)
- `test-suite/cmmi-regression/test_supervisor_llm_delegation.py` (1.4c)
- _(deferred — `bin/cmmi-logs-from-queue.py`, only if 3.5 ever authorised)_

**Modified (5 files):**
- `bin/cmmi-msg-bridge.py` (`--max-age-days` arg in 3.1a)
- `bin/cmmi-metrics-ingest.py` (3 new KPI collectors in 4.1B prep)
- `bin/cmmi-audit.sh` (`[QPM]` step in 4.AUD)
- `src/pycsl/agents/agent-feature-supervisor.py` (`--allow-llm-delegation` + rollback helper in 1.4a + 1.4b; queue reader switch in 3.4)
- `projects/pycsl/PROJECT.md` (Bridge schedule subsection in 3.1)

**Reused (no rewrite):**
- `src/pycsl/agents/llm_client.py:llm_generate` (1.4a delegation call)
- `bin/cmmi-msg-bridge.py` (3.1 daily run; already built)
- `bin/cmmi-metrics-ingest.py` (4.1B prep extends; doesn't rewrite)
- `bin/cmmi-audit.sh` (4.AUD adds a step; doesn't rewrite)
- `coordinator.py` exit-code convention (1.4b inherits 74/75/76)
- `git` subprocess pattern from `agent-stdlib-annotate.py:_rollback`

---

## Execution order

```
Now (today, ~6 hours of code + tests):
  1. [3.1a]   Add --max-age-days to cmmi-msg-bridge.py             20 min
  2. [3.1]    Build bin/cmmi-bridge-daily.sh + cron docs           20 min
  3. [4.1B p] Extend cmmi-metrics-ingest.py with 3 collectors      4 hours
  4. [4.AUD]  Wire [QPM] step into bin/cmmi-audit.sh               1 hour

Week 1 (~3 days):
  5. [3.2]    src/pycsl/agents/queue_reader.py                     1 day
  6. [3.3]    Synthetic-queue fixture + test_queue_reader.py       1 day
  7. [4.1B]   bin/cmmi-qpm-charts.py — chart + table emission      2 days
              (overlaps with 3.2/3.3)

Week 2 (~3 days):
  8. [4.1C]   Western Electric rule detection                      1 day
  9. [1.4a]   --allow-llm-delegation flag + prompt scaffold        1 day
 10. [1.4b]   Per-phase git-tag + rollback helper                  1 day

Week 3 (~1 day):
 11. [1.4c]   Mock-LLM end-to-end tests                            1 day

Week 4+ (gated):
 12. [3.4]    Supervisor reader switch (5-min edit; gated on
              ≥14 days of dual-write since [3.1] start)            5 min
 13. [4.AUTO] First strong-signal QPM report (no work; emitted by
              cmmi-qpm-charts.py once snapshots[].len >= 8)        n/a

Never auto-executed:
  -. [3.5]    coordinator.py write-path decommission — requires
              explicit user authorisation per follow-up.md hard rule

  -. [1.4d]   Watch-mode for proposed-features (optional)
```

Total scoped effort: **~7 days of code + ~2-3 days of tests,
across 3 weeks**. Then the system runs on autopilot until the
8-snapshot threshold flips QPM into preliminary mode at week 8.

---

## Verification

Every PR in this plan extends `bin/cmmi-audit.sh` to keep the gate
authoritative. After all items land, the audit reports:

```
[C8.1+2] No source duplication                 OK
[C8.3]   pycsl-include anchors resolve         OK
[C8.4]   L4 indices match def counts           OK
[C8.5]   Squeeze coverage                      OK   (9/9 + 2 glue)
[REG]    itertools.cycle regression            OK   (9+ tests after 3.3+1.4c)
[QPM]    snapshot count + signal status        OK   (informational: weak/preliminary/strong)
[lang]   Language-surface doc coherency        OK
```

**Per-item acceptance:**

| Item | Acceptance command | Expected |
|---|---|---|
| 3.1 | `bin/cmmi-bridge-daily.sh && ls projects/pycsl/message-queues/` | ≥1 agent inbox dir exists |
| 3.2 | `python3 -c 'from queue_reader import iter_messages; list(iter_messages("agent-stdlib-annotate"))'` | non-empty list of dicts with `schema == pycsl-cmmi-bridge-v1` |
| 3.3 | `pytest test-suite/cmmi-regression/test_queue_reader.py -v` | 5/5 PASS |
| 3.4 | `bin/agent-feature-supervisor --feature-file missing-iter-feature.md --skip-gate` after switch | still exits 75; halt-report cites queue messages instead of `metrics/logs/` |
| 1.4a | `bin/agent-feature-supervisor --help` mentions `--allow-llm-delegation` | flag visible |
| 1.4b | `pytest test-suite/cmmi-regression/test_supervisor_llm_delegation.py::test_rollback_on_gate_fail -v` | PASS; per-phase tag absent after rollback |
| 1.4c | `pytest test-suite/cmmi-regression/test_supervisor_llm_delegation.py -v` | 2/2 PASS (success path + rollback path) |
| 4.1B | `bin/cmmi-qpm-charts.py && cat projects/pycsl/docs/reports/qpm-report-001.md` | report exists; "weak signal (n=K)" tag visible at top of each chart |
| 4.1C | seed a fake snapshot history with a 3σ excursion; `bin/cmmi-qpm-charts.py` | "Signals" section lists the WE rule hit |
| 4.AUD | `bin/cmmi-audit.sh` | 7/7 gates pass (was 6/6) |

---

## Risks specific to this plan

- **Bridge volume explosion.** Without `--max-age-days`, daily runs
  re-mirror the full 81k-message backlog on every fresh checkout.
  Mitigation: 3.1a adds the flag; default 30 days; bridge cursor
  file in git so subsequent runs are incremental.
- **LLM produces a diff that applies cleanly but breaks semantics.**
  Mitigation: 1.4b rollback policy + the verification gate. The
  gate runs `bin/run-reference-tests.sh` which exercises the actual
  pycsl pipeline — a semantically-bad change shows up as a corpus
  regression and triggers rollback.
- **`git apply` corner cases** (whitespace, line-endings, missing
  trailing newline). Mitigation: invoke as
  `git apply --whitespace=nowarn --recount` and check with
  `git apply --check` first; if the check fails, halt with exit 74
  before any tree mutation.
- **WE rule false positives on the first 8-20 snapshots.** Mitigation:
  "preliminary" tag in the report makes the uncertainty explicit;
  4.AUD step is informational-only (never fails the audit).
- **Stale snapshot detection at boundary.** A snapshot taken at
  exactly 10 days ago might or might not flag. Mitigation: use
  strict `< 10` days for "fresh", `>= 10` for "stale"; document
  the boundary in the report header.
- **1.4 expanded blast radius.** Even with the deny-list, LLM
  delegation lets the supervisor touch non-load-bearing source.
  Mitigation: `--allow-llm-delegation` defaults OFF; the human
  enables it per-feature only after reviewing the plan's target
  list.

---

## Out of scope

- Item 3.5 — `coordinator.py` write-path decommission. Permanent
  steady state is acceptable; sunset only on user authorisation.
- Item 1.4 with parallelism. Phases run serially; the supervisor
  never delegates two phases simultaneously even when their target
  files don't overlap.
- Phase 1.5 — autonomous PR creation. The supervisor leaves edits
  in the working tree; human stages, commits, and pushes.
- Profile-P modifications. This plan extends the existing tooling;
  it does NOT touch `projects/pycsl/PROJECT.md` `spec_kind:` or
  `squeeze_owners:`. The 5-level binding and BL plan remain as
  declared in `cmmi-tailoring-plan.md`.
- QPM strong-signal alerts to external systems. The QPM step writes
  reports to disk only; integration with email/Slack/etc. is a
  separate decision.
- A second-language `*csl` port driven by this plan. The 9-system
  topology stays PyCSL-specific; gocsl/ccsl/etc. inherit the
  pattern but instantiate their own `projects/<lang>csl/PROJECT.md`.

---

## What this plan does NOT do

- Does not pre-implement Item 3.5 (coordinator decommission).
- Does not change Profile-P or the BL plan binding.
- Does not commit to landing Item 1.4 — the flag defaults off, so
  shipping the code adds no automatic behavior.
- Does not introduce any new normative documents under `docs/`.
- Does not modify any `pycsl-*` domain skill.
- Does not retrofit the 8 `pycsl-*` skills to CMMI §1-§6 format
  (per `should-we-cmmi-or-not.md` §6 Rule 3).
- Does not add a watch loop on `proposed-features/` (1.4d) unless
  explicitly requested — manual invocation works fine.

---

## References

- [`cmmi-tailoring-plan.md`](cmmi-tailoring-plan.md) — the parent
  plan that established Profile-P + the 9-system topology.
- [`cmmi-tailoring-plan-follow-up.md`](cmmi-tailoring-plan-follow-up.md)
  — Items 1.1-1.3 + 2 + 4.1A; this plan picks up the 3 explicit
  deferrals.
- [`better-agent.md`](better-agent.md) — the canonical design for
  the supervisor (Items 1.4a-c instantiate Phase 3b of that doc).
- [`missing-iter-feature.md`](missing-iter-feature.md) — the
  worked-example feature plan whose Phase 3 + Phase 4 are the
  natural first targets for Item 1.4 delegation (no load-bearing
  hits in those phases per Item 2's regression test).
- [`should-we-cmmi-or-not.md`](should-we-cmmi-or-not.md) §8 risk 3
  — "two substrates indefinitely is a bug" (the rationale for
  Phase 2 cutover at all).
- `bin/cmmi-audit.sh` — the composite gate every item extends.
- `bin/cmmi-msg-bridge.py` — the bridge whose daily run starts the
  2-week clock that gates 3.4.
- `bin/cmmi-metrics-ingest.py` — extended in 4.1B prep with 3 new
  collectors.
- `src/pycsl/agents/agent-feature-supervisor.py` — extended in 1.4a
  + 1.4b + 3.4 (one combined PR or three small PRs — author's
  choice).
- `src/pycsl/agents/coordinator.py` — exit-code precedent
  (72/73/74/75/76); not modified by this plan.
