# CMMI Tailoring Plan — Follow-Up Work Items

## Context

The execution of [`cmmi-tailoring-plan.md`](cmmi-tailoring-plan.md)
landed the scaffold (315 files under `projects/pycsl/`), the 5 new
`bin/cmmi-*` tools, the Profile-P rows in 10 skills, and verified
5/5 gates. Four items were explicitly deferred because they either
depend on `better-agent.md` deliverables, are operational decisions,
or require time to accumulate data:

1. **`agent-feature-supervisor.py` + `--detect-gaps` for
   `agent-stdlib-annotate.py`** — Phase 1+ of `better-agent.md`.
2. **Phase D check 7** — regression test against the 2026-05-31
   13:47:22 `itertools.cycle` incident; depends on (1).
3. **Phase 2 of the `communication`-skill transition** — sunset the
   `metrics/` substrate; depends on (1).
4. **Phase 1+ of `cmmi-quantitative-mgmt`** — control charts; needs
   ≥8 weekly snapshots, today is snapshot #1.

This plan specifies how to execute each, in dependency order, with
concrete file paths and acceptance criteria.

The state we're starting from (verified by `bin/cmmi-audit.sh` on
2026-05-31):

| Asset | Status |
|---|---|
| `metrics/logs/*.log` | 164 files, 101,544 lines |
| `metrics/stdlib-gap-report.json` | **does not exist yet** (Phase 1 deliverable) |
| `SY6-PycslLib` L3-ceiling notes | 12 (the `# cite:_note:` markers the Reconciliator must aggregate) |
| `projects/pycsl/docs/metrics/metrics-store.json` | 1 snapshot (today) |
| `projects/pycsl/message-queues/` | empty (bridge ran `--dry-run` only) |
| `bin/agent-stdlib-annotate` | exists; **no `--detect-gaps` flag yet** |
| `src/pycsl/agents/agent-feature-supervisor.py` | **does not exist yet** |
| `proposed-features/` | exists with README; no drafts yet |

---

## Dependency graph

```
                ┌─────────────────────────────────────────────────┐
                │ (1) better-agent.md Phase 1: gap detection       │
                │     in agent-stdlib-annotate.py (--detect-gaps)  │
                │     → metrics/stdlib-gap-report.json             │
                └────────────────┬────────────────────────────────┘
                                 │
                ┌────────────────▼────────────────────────────────┐
                │ (1) better-agent.md Phase 2: --propose-feature  │
                │     → proposed-features/missing-*-feature.md     │
                └────────────────┬────────────────────────────────┘
                                 │
                ┌────────────────▼────────────────────────────────┐
                │ (1) better-agent.md Phase 3: supervisor scaffold │
                │     → src/pycsl/agents/agent-feature-supervisor  │
                │     → bin/agent-feature-supervisor               │
                └────┬───────────────────────────────────────────┬┘
                     │                                            │
        ┌────────────▼────────────┐               ┌──────────────▼──────────┐
        │ (2) Phase D check 7 —    │               │ (3) communication Phase  │
        │     regression test on   │               │     2 sunset — supervisor│
        │     itertools.cycle      │               │     reads from message   │
        │     incident             │               │     queue, not metrics/  │
        └──────────────────────────┘               └──────────────────────────┘

        (4) cmmi-quantitative-mgmt Phase 1 — independent of (1)–(3);
            blocked only on clock (≥8 weekly snapshots → ≥8 weeks from today).
```

(1) is the critical-path item. (2) and (3) become possible after (1)
Phase 3 lands. (4) runs on its own timeline; the first concrete
action (wiring weekly cron) can ship today.

---

## Item 1 — `agent-feature-supervisor.py` + `--detect-gaps`

Concrete instantiation of `better-agent.md` Phases 1-3. The full
design is in that document; this section sizes and orders the
implementation.

### Phase 1.1 — `--detect-gaps` flag (2 days, smallest viable slice)

**Goal:** Scan existing `# cite:_note:` lines in `src/pycsl_lib/`,
classify by gap category, write `metrics/stdlib-gap-report.json`.
**No proposals, no orchestration.** Just visibility.

| File | Change |
|---|---|
| `src/pycsl/agents/agent-stdlib-annotate.py` | Add `--detect-gaps` arg. New `_classify_gap(note: str) -> str` heuristic classifier (one regex per category; default `unclassified`). New `_scan_existing_notes(lib_root: Path) -> dict[str, list[tuple[str, str]]]` that walks `src/pycsl_lib/*.py`, extracts every `# cite:_note: <text>` line, classifies. Aggregates into `{category: count, examples: [(stub_path, note_text), ...]}`. Writes `metrics/stdlib-gap-report.json`. |
| `bin/agent-stdlib-annotate` | Document new flag in `--help` text. |

Heuristic taxonomy (Phase 1.1 — keep small, expand later):

| Category | Regex trigger |
|---|---|
| `iterator-semantics` | `\b(iterator\|infinite\|yields\|lazy sequence\|generator)\b` |
| `regex-semantics` | `\b(regex\|regular expression\|pattern[- ]match)\b` |
| `higher-order` | `\b(callback\|predicate function\|function argument\|higher[- ]order)\b` |
| `string-content` | `\b(string contents\|format string\|encoding)\b` |
| `io-side-effect` | `\b(file system\|file handle\|socket\|stream\|I/O)\b` |
| `non-deterministic` | `\b(random\|time\|clock\|uuid)\b` |
| `unclassified` | none of the above |

The 12 existing notes in `SY6-PycslLib` are the first real input;
the classifier MUST categorise `itertools.cycle` as
`iterator-semantics` for this slice to be considered correct.

**Acceptance criterion (Phase 1.1):**
```bash
bin/agent-stdlib-annotate --detect-gaps
cat metrics/stdlib-gap-report.json | jq '.categories["iterator-semantics"].count'
# expected: >= 1 (cycle, count, repeat, ...)
```

**Effort:** 2 days. **Shippable as a standalone PR.**

### Phase 1.2 — `--propose-feature` flag (3 days)

Threshold-gated draft generation. Runs after `--detect-gaps`.

| File | Change |
|---|---|
| `config/skills/agent-stdlib-annotate/references/feature-plan-template.md` (NEW) | Extracted from `missing-iter-feature.md` with `{{slot}}` placeholders for: anchor function, scope table, design options, recommended design, implementation surface, suggested first PR. |
| `src/pycsl/agents/agent-stdlib-annotate.py` | Add `--propose-feature [category]` arg. New `_emit_proposal(category: str, report: dict) -> Path` that loads the template, fills slots from the report's `examples` field, dispatches one structured LLM call for the design-options section, writes `proposed-features/missing-<category>-feature.md` with `STATUS: DRAFT` header. |
| `proposed-features/README.md` (exists) | No change — already documents the DRAFT → APPROVED workflow. |

Threshold default: `≥5` stuck functions per category (configurable
via `--proposal-threshold N`). The 12 iterator notes today comfortably
exceed this — Phase 1.2's first real run should produce a draft
`proposed-features/missing-iterator-semantics-feature.md` that reads
structurally similar to the human-authored `missing-iter-feature.md`.

**Acceptance criterion (Phase 1.2):**
```bash
bin/agent-stdlib-annotate --propose-feature iterator-semantics
diff <(head -20 proposed-features/missing-iterator-semantics-feature.md) \
     <(head -20 missing-iter-feature.md)
# expected: similar section structure (gap → scope → design options),
# possibly different prose. Acceptance is soft — human reads the draft.
```

**Effort:** 3 days. **Ships as a follow-up PR after 1.1.**

### Phase 1.3 — supervisor scaffold, gate-only (5 days)

The new `agent-feature-supervisor.py`. Initial scope: **orchestrate
the verification gate; halt with "human-needed" on every code-edit
phase.** No coding-LLM delegation yet.

| File | Change |
|---|---|
| `src/pycsl/agents/agent-feature-supervisor.py` (NEW) | Main supervisor. Watches `proposed-features/` for `STATUS: APPROVED` transitions (or — for v1 — accepts a `--feature-file <path>` arg). Parses the "Implementation surface" section into a phase list. For each phase: tag `feature-<slug>-phase-<N>-start`, run verification gate, emit halt-report. Always raises "human-needed" for every phase in v1. |
| `config/agents/agent-feature-supervisor.md` (NEW) | Persona spec: responsibilities, scope, safety perimeter (mirrors the table in `better-agent.md` §"Safety perimeter"). |
| `config/agents-config.json` | New `skill-feature-supervisor` key with retrieval queries for `pycsl-how-to-develop`, `pycsl-doc-coherency`, `pycsl-stdlib-coverage`. |
| `bin/agent-feature-supervisor` (NEW) | Thin bash wrapper, mirrors `bin/agent-stdlib-annotate`. |
| `config/skills/agent-stdlib-annotate/references/load-bearing-files.md` (NEW) | Explicit deny-list: `Module2_Parser.py`, `module6_whyml/expressions.py`, `module6_whyml/preamble.py`, `module6_whyml/types.py`. Phases that touch these files always raise human-needed. |

Verification gate (per `better-agent.md` §"Verification gate"):
```
1. pytest -q tests/
2. bin/run-reference-tests.sh
3. bin/doc-coherency.py --check
4. bin/cmmi-audit.sh
5. bin/stdlib-coverage-report.py --diff
6. bin/agent-stdlib-annotate --dry-run --module <anchor>
```

Exit codes (extend `coordinator.py`'s 72/73 convention):
- `74` — phase gate failure
- `75` — human-needed signal raised
- `76` — rollback failure

**Acceptance criterion (Phase 1.3):**
```bash
# Move the human-authored missing-iter-feature.md as the test case
cp missing-iter-feature.md proposed-features/test-feature.md
# (manually add STATUS: APPROVED if checking the watch loop, or use --feature-file)
bin/agent-feature-supervisor --feature-file proposed-features/test-feature.md
# expected: exit 75 (human-needed), with halt-report at
# metrics/feature-supervisor/test-feature/halt-report.md naming Phase 1
# files (Module2_Parser.py is load-bearing → human-needed)
```

**Effort:** 5 days. **Ships as a third PR.**

### Phase 1.4 — coding-LLM delegation (3 days, optional)

| File | Change |
|---|---|
| `src/pycsl/agents/agent-feature-supervisor.py` | For phases not on the load-bearing deny-list, generate a phase-scoped prompt (template embedded), dispatch via `llm_generate`, apply output with `git apply`, run the gate. Halt with exit 74 on gate failure (rollback via per-phase git tag). |

This is the optional Phase 3b from `better-agent.md`. Defer until 1.3 has been exercised in anger. Today's recommendation: **freeze
on 1.3 indefinitely if it covers 80% of the manual overhead.**

### Total effort: 10 days (Phases 1.1+1.2+1.3) or 13 days with 1.4.

### Critical files

**New:**
- `src/pycsl/agents/agent-feature-supervisor.py`
- `config/agents/agent-feature-supervisor.md`
- `bin/agent-feature-supervisor`
- `config/skills/agent-stdlib-annotate/references/feature-plan-template.md`
- `config/skills/agent-stdlib-annotate/references/load-bearing-files.md`

**Modified:**
- `src/pycsl/agents/agent-stdlib-annotate.py` (add 2 flags, ~150 LOC delta)
- `bin/agent-stdlib-annotate` (--help text)
- `config/agents-config.json` (one new skill-* key)

**Reused (no rewrite):**
- `src/pycsl/agents/llm_client.py:llm_generate`
- `src/pycsl/agents/coordinator.py` (exit-code convention, loop detection)
- `src/pycsl/agents/agent-stdlib-annotate.py:_parse_llm_block` (extend to surface `# cite:_note:` lines — Phase 1.1 adds the extension)
- `bin/stdlib-coverage-report.py`
- `bin/doc-coherency.py`
- `bin/run-reference-tests.sh`
- `bin/cmmi-audit.sh`

### Risks specific to (1)

- **Classifier overfits to the 12 existing notes.** The regex
  taxonomy is small. Mitigation: report classifier confidence
  (top-2 candidates) in `--detect-gaps` JSON; add `--review-classifications`
  human-in-loop mode before threshold counting.
- **Phase 1.2 LLM draft reads nothing like `missing-iter-feature.md`.**
  Mitigation: ship 1.2 with a single human review of the first
  draft; iterate on the template + prompt until the next draft is
  acceptable before exposing the flag in CI.
- **Watch-loop deadlock (Phase 1.3).** Mitigation: v1 uses
  `--feature-file <path>` arg only; watch loop is Phase 1.5
  follow-up if needed.

---

## Item 2 — Phase D check 7 (regression test on the
2026-05-31 13:47:22 `itertools.cycle` incident)

**Depends on:** Item 1 Phase 1.2 (`--propose-feature`) at minimum.
Optionally exercises Item 1 Phase 1.3 (supervisor) for a true
end-to-end test.

### Goal

Codify the user's acceptance criterion ("agents should now spot what
only the human spotted before") as a deterministic, replayable
regression test. Wire it into the CI gate.

### Approach: snapshot replay, not live agent run

The incident is a *historical event*. We can't replay the LLM call
deterministically. Instead, freeze the artefact the incident
produced:

- The stub `src/pycsl_lib/itertools.py:cycle` with its
  `#@ \trusted reviewer: python-stdlib` + `# cite:_note:` block.

And test that the **detector** classifies it correctly.

### Implementation

| File | Change |
|---|---|
| `test-suite/cmmi-regression/test_itertools_cycle_detection.py` (NEW) | A `pytest` test that:<br/>1. Runs `bin/agent-stdlib-annotate --detect-gaps` against a fixture copy of `src/pycsl_lib/itertools.py` containing the original `cycle` stub.<br/>2. Asserts the resulting `metrics/stdlib-gap-report.json` contains `iterator-semantics` with count ≥1 and `cycle` in the examples list.<br/>3. Runs `--propose-feature iterator-semantics`.<br/>4. Asserts a `proposed-features/missing-iterator-semantics-feature.md` is created with `STATUS: DRAFT`. |
| `test-suite/cmmi-regression/fixtures/itertools-incident-snapshot.py` (NEW) | Frozen copy of `src/pycsl_lib/itertools.py:cycle` as of 2026-05-31 13:47:22 — the contract-block snapshot in `missing-iter-feature.md` §"The gap" works as the canonical fixture. |
| `bin/cmmi-audit.sh` | Add a new check `[REG] itertools.cycle regression` that runs `pytest test-suite/cmmi-regression/ -q` and reports PASS/FAIL. Run it after the existing 5 checks. |
| `projects/pycsl/BL/tests/main.md` | Update `BL-AT-REG-001` row: status changes from "DEFERRED" to "OK once Item 1.1+1.2 land". |

### Acceptance criterion

```bash
bin/cmmi-audit.sh
# Summary: 6 passed, 0 failed, 0 skipped  (was 5/5)
```

The regression test is a **single test**, not a suite — its purpose
is to catch regression of the gap-detection pipeline. Extra
gap-detection tests live under `test-suite/cmmi-regression/` over
time as new incidents accumulate.

### Effort: 1 day after Item 1 Phase 1.2 lands.

### Risks

- **False positives if `_classify_gap` taxonomy widens.** Mitigation:
  the test asserts `iterator-semantics` specifically, not "any
  classification"; widening the taxonomy doesn't break this test as
  long as `cycle` still maps to iterator-semantics.
- **Fixture goes stale if `src/pycsl_lib/itertools.py:cycle` is
  edited** (e.g., promoted to L4 once the iterator-semantics feature
  lands per `missing-iter-feature.md`). Mitigation: the fixture is a
  *frozen snapshot*, not a live reference; the test isolates from the
  live `src/pycsl_lib/` tree by using `--scan-path <fixture>` (a new
  arg to `agent-stdlib-annotate` added in Phase 1.1).

---

## Item 3 — Phase 2 of the `communication`-skill transition (sunset `metrics/` substrate)

**Depends on:** Item 1 Phase 1.3 (supervisor) — the supervisor is
the first downstream consumer that should switch from `metrics/`
to the queue.

### Decision gate: when to start Phase 2

Per the `communication` skill's Profile-P tailoring row, Phase 2
begins when:

1. `agent-feature-supervisor.py` is live (Item 1 Phase 1.3).
2. The supervisor has produced ≥10 verification-gate runs and ≥1
   `proposed-features/` draft has been APPROVED end-to-end.
3. `bin/cmmi-msg-bridge.py` has run successfully against a real
   production snapshot for ≥2 weeks without complaint.

These thresholds prevent a half-baked supervisor from being trapped
behind a queue substrate it can't read reliably.

### Phase 2 work plan

| Step | Action | Risk |
|---|---|---|
| 2.1 | `bin/cmmi-msg-bridge.py` runs daily via a new cron entry (or `bin/run-reference-tests.sh` invocation). | Low — already validated by `--dry-run` (81,702 messages, 119 agents). |
| 2.2 | Modify `agent-feature-supervisor.py` to read from `projects/pycsl/message-queues/<agent>/inbox-from-logs/*.json` instead of `metrics/logs/*.log`. Use the `source_uri` field for citations back to the original log line. | Medium — the supervisor's parser needs a JSON-message format instead of free-text log lines. |
| 2.3 | Decommission `metrics/logs/` writes from `coordinator.py` IF the supervisor consumes the queue cleanly. **Decision point — do NOT auto-execute.** | High — `coordinator.py` is the central agent orchestrator; breaking its log path breaks observability. |
| 2.4 | Sunset path: `metrics/logs/` becomes a *derived view* generated from the queue via a new `bin/cmmi-logs-from-queue.py` (one-way mirror in the reverse direction, for backward compatibility with humans grepping logs). | Low — purely additive. |

### Hard rule

**Do not enter Phase 2.3 (decommissioning) without explicit
authorization.** The dual-write phase (2.1 + 2.2) is the safe
steady state; we can live there indefinitely. The "sunset" framing
in the original skill is aspirational — operationally, dual-write
may be the right end state if no concrete pain is felt.

### Critical files

**New:**
- (Optional) `bin/cmmi-logs-from-queue.py` — only if Phase 2.3 is ever
  authorized.
- A cron / Makefile entry running `bin/cmmi-msg-bridge.py` daily.

**Modified:**
- `src/pycsl/agents/agent-feature-supervisor.py` — switch reader from
  `metrics/logs/` to the queue (Phase 2.2).
- `src/pycsl/agents/coordinator.py` — only if Phase 2.3 lands;
  high-risk edit.

### Acceptance criterion (Phase 2.2 only)

```bash
# After Phase 2.2 lands:
bin/agent-feature-supervisor --feature-file proposed-features/<approved>.md
grep 'source_uri' metrics/feature-supervisor/<feature>/phase-1.log
# expected: every cited event references projects/pycsl/message-queues/...
# not metrics/logs/...
```

### Effort: 2 days for Phase 2.1+2.2. Phase 2.3 is a separate
authorization, not part of this work.

### Risks

- **Bridge cursor corruption.** The bridge tracks `.bridge-cursor.json`
  per-agent. If corrupted, `--rebuild` re-mirrors from scratch (81k
  messages first time). Mitigation: cron entry runs with
  `flock` to prevent concurrent runs; cursor file is in git, not in
  `.gitignore`.
- **Queue volume explosion.** 81k messages → 81k JSON files on disk.
  Mitigation: add `--max-age-days N` to the bridge so only recent
  messages are mirrored; periodic archive via the
  `communication`-skill's archive convention.

---

## Item 4 — Phase 1+ of `cmmi-quantitative-mgmt` (control charts)

**Depends on:** clock time — ≥8 weekly snapshots in
`projects/pycsl/docs/metrics/metrics-store.json`. Today is snapshot
#1 (2026-05-31). Earliest Phase 1 start: 2026-07-26 (8 weeks out).

### Goal

Build SPC (Statistical Process Control) charts for 4 PyCSL-priority
KPIs declared in `cmmi-tailoring-plan.md` §8:

1. Proof-success rate per system per week
2. Agent retry-count drift
3. L3-ceiling rate trend per system
4. Doc-coherency events per week

Once a chart has ≥8 data points, compute mean μ, σ, control limits
(UCL = μ + 3σ, LCL = max(0, μ − 3σ)). Flag Western Electric rule
violations (1 point > 3σ; 2 of 3 > 2σ; 8 in a row on same side of μ).

### Phase 1A — Automate weekly snapshots (today, 30 minutes)

| File | Change |
|---|---|
| `bin/cmmi-weekly-snapshot.sh` (NEW) | One-liner wrapper around `bin/cmmi-metrics-ingest.py --weekly`. Designed to be the cron entry. |
| User's crontab (manual setup, not in repo) | `0 6 * * 1 cd ~/git/pycsl && bin/cmmi-weekly-snapshot.sh >> metrics/cron.log 2>&1` (Mondays 06:00). |
| `projects/pycsl/PROJECT.md` | Add a "Snapshot schedule" subsection documenting the cron entry (audit trail). |

**Acceptance criterion (Phase 1A):**
```bash
bin/cmmi-weekly-snapshot.sh
python3 -c "import json; n=len(json.load(open('projects/pycsl/docs/metrics/metrics-store.json'))['snapshots']); print(f'snapshots: {n}')"
# expected: snapshots: 1 (or more, if today's snapshot was already added)
```

**This can be done today.** It's the only Phase 4-item action that
isn't blocked.

### Phase 1B — Chart generation (2 days, gated on ≥8 snapshots)

| File | Change |
|---|---|
| `bin/cmmi-qpm-charts.py` (NEW) | Read `metrics-store.json`. For each of the 4 KPIs, extract the time series, compute μ + σ + control limits, emit a Markdown table + an ASCII-art (or matplotlib if available) chart. Output to `projects/pycsl/docs/reports/qpm-report-<NNN>.md`. |
| `config/skills/cmmi-quantitative-mgmt/SKILL.md` §4.T | Update Phase 0 → Phase 1 transition condition: when `len(snapshots) >= 8`, the tool exits 0 and prints "ready for Phase 1"; until then, exits 0 with "Phase 0 — snapshot accumulation". |
| `bin/cmmi-audit.sh` | Add (after `[REG]`) `[QPM] snapshot count`: prints current count and Phase 0/1 status. Does not gate on it. |

### Phase 1C — Western Electric rule detection (1 day, after Phase 1B is exercised)

| File | Change |
|---|---|
| `bin/cmmi-qpm-charts.py` | Add rule detection: for each chart, scan for the 4 standard WE rules (1 point >3σ, 2 of 3 >2σ, 4 of 5 >1σ, 8 in a row on same side). Emit a "Signals" section to the QPM report. |
| `bin/cmmi-audit.sh` | If `[QPM]` finds rule violations after Phase 1B, escalate via `cmmi-glue` Workflow 3 (write a report under `projects/pycsl/docs/audits/qpm-signal-<NNN>.md`). |

### Total effort

- Phase 1A: 30 min (today).
- Phase 1B: 2 days (≥8 weeks from now).
- Phase 1C: 1 day (≥8 weeks + Phase 1B done).

### Critical files

**New:**
- `bin/cmmi-weekly-snapshot.sh` (Phase 1A)
- `bin/cmmi-qpm-charts.py` (Phase 1B+1C)

**Modified:**
- `projects/pycsl/PROJECT.md` (cron schedule docs)
- `config/skills/cmmi-quantitative-mgmt/SKILL.md` (Phase 0 → 1 transition wording)
- `bin/cmmi-audit.sh` (`[QPM]` check)

### Risks

- **Cron entry silently fails.** Mitigation: `bin/cmmi-weekly-snapshot.sh`
  exits non-zero on failure; the `[QPM]` check in `bin/cmmi-audit.sh`
  notices stale snapshots (no new entry in the last 8 days → flag).
- **Insufficient data for stable baselines.** Per `cmmi-quantitative-mgmt`
  §4.E, 8 snapshots is the *minimum*; meaningful UCL/LCL needs more.
  Mitigation: Phase 1B's first run prints control limits with a "weak
  signal" tag if `n < 20`; flip to "strong" after `n >= 20`.
- **Disk costs.** Each weekly snapshot is ~5 KB based on today's
  output. 52 weeks × 5 KB ≈ 260 KB/year — negligible.

---

## Execution order across all 4 items

```
Now (today):
  [4.1A] bin/cmmi-weekly-snapshot.sh + cron entry  (30 min)

Within 2 weeks:
  [1.1] --detect-gaps                              (2 days)
  [1.2] --propose-feature                          (3 days)
  [2]   Phase D check 7 regression test            (1 day)
  → PR #1 ships items [1.1] + [1.2] + [2] together; 6 days total.

Within 4 weeks:
  [1.3] supervisor scaffold (gate-only)            (5 days)
  → PR #2 ships [1.3]; 5 days.

Within 8 weeks (gated on actual operational signal):
  [3.1+3.2] communication Phase 2 (bridge + read)  (2 days)
  [1.4] coding-LLM delegation (optional)           (3 days)
  → PR #3 ships these as separate authorisations.

Week 8+ (gated on clock):
  [4.1B] cmmi-qpm-charts.py                        (2 days)
  [4.1C] Western Electric rule detection           (1 day)
  → PR #4 ships [4.1B] + [4.1C] together.

NOT YET / requires authorisation:
  [3.3] coordinator.py write-path decommission     (separate)
```

Total scoped effort: **~16 days** spread over 8 weeks. **Critical
path:** Item 1 (10 days minimum). Items 2, 3.1+3.2 unlock as soon as
their dependencies in Item 1 land.

---

## Cross-cutting verification

For every PR landing one of these items:

1. `bin/cmmi-audit.sh` exits 0 (all gates pass).
2. `bin/doc-coherency.py --check` exits 0.
3. The PR's commit message includes `role: specifier|verifier|reconciliator`
   tag per Profile-P single-developer CCB convention.
4. If the PR adds a new bin/ tool, `bin/cmmi-audit.sh` is extended
   to invoke it (so future PRs can rely on the gate).
5. If the PR adds a new contract directive or `#@`-related feature,
   the existing `bin/doc-coherency.py` discovers it automatically;
   no extra wiring.

The verification suite from `cmmi-tailoring-plan.md` §Verification
remains the acceptance gate; Item 2 just adds check #7 (regression
test) to it.

---

## What this plan does NOT do

- Does not pre-implement the deferred work; it is a roadmap for
  *executing* the deferrals when the user is ready.
- Does not authorise Item 3.3 (`coordinator.py` write-path
  decommission). That requires a separate decision after Phase
  2.1+2.2 has run for ≥2 weeks without complaint.
- Does not specify the matplotlib-vs-ASCII chart choice for Item 4
  Phase 1B — that's a small-effort call made at implementation
  time.
- Does not address the `agent-feature-supervisor.py` watch-loop
  (Phase 1.5) or asynchronous polling — v1 uses `--feature-file`
  arg only.
- Does not introduce any new tailoring profiles or amend Profile-P;
  Profile-P as declared in `PROJECT.md` covers all 4 items.
- Does not commit to landing all 4 items; each is independently
  authorisable. Item 4.1A alone is a meaningful improvement
  (closes the snapshot-accumulation loop).

---

## References

- [`cmmi-tailoring-plan.md`](cmmi-tailoring-plan.md) — the parent
  plan whose execution surfaced these deferrals.
- [`better-agent.md`](better-agent.md) — the full design for the
  Reconciliator (Item 1's design source).
- [`missing-iter-feature.md`](missing-iter-feature.md) — the
  human-authored fixture the regression test (Item 2) is built
  against.
- [`should-we-cmmi-or-not.md`](should-we-cmmi-or-not.md) — the
  recommendation envelope; §"Hard rule" governs Item 3.3
  authorisation.
- `projects/pycsl/PROJECT.md` — declares Profile-P and the
  squeeze ownership; documents the cron schedule once Item 4.1A
  lands.
- `config/skills/csl-from-scratch/SKILL.md` — the BL plan;
  unchanged by this follow-up.
- `bin/cmmi-audit.sh` — the gate every item extends.
- `src/pycsl/agents/coordinator.py` — the precedent for exit-code
  convention (72/73 → 74/75/76) that Item 1.3 extends.
