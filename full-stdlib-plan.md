# Full stdlib annotation — launch plan

**Owner:** SY6-PycslLib (Profile M, owning Squeezes S1 + S8)
**BL anchor:** `csl-from-scratch` §0.5 S1 (CSL contracts) + S8 (real-world test cases)
**Source of truth:** `test-suite/library_reference/*.rst` (331 files,
5,993 signatures parsed from `.. function::` / `.. class::` /
`.. method::` / `.. exception::` / `.. data::` directives)
**Target end state:** every importable stdlib module has a stub in
`src/pycsl_lib/` with at least L2 contracts (signature + `\trusted`);
modules that the annotator can promote reach L4 (full ensures).
**STATUS: APPROVED — awaiting human approval to launch Phase A.**

---

## Context

The user has asked: can we launch the complete annotation of the
Python stdlib today, using `test-suite/library_reference/` as the
source of truth?

**Yes — the infrastructure is in place.** Two tools already exist:

1. `bin/generate_lib_stubs.py` — reads `.rst` files, emits
   `src/pycsl_lib/<module>.py` scaffolds with `\trusted` annotations
   and semantic postconditions from English descriptions.
2. `bin/agent-stdlib-annotate --all` — iterates every stub in
   `src/pycsl_lib/` and promotes L2 → L4/L5.

Today, `src/pycsl_lib/` has stubs for **37 modules**;
`test-suite/library_reference/` has **331 `.rst` files** covering
~300 importable modules (after excluding category pages and
asyncio sub-pages, per `bin/generate_lib_stubs.py:NON_MODULE_RSTS`
and `ASYNCIO_SUBPAGES`).

**The gap: ~263 importable modules without stubs yet.** Closing
that gap is what "launch the complete stdlib annotation" means.

---

## Sizing the work

| Axis | Value |
|---|---|
| Total `.rst` files | 331 |
| Non-module / sub-page exclusions | ~40 |
| Net importable modules | ~290 |
| Total signatures (parseable directives) | 5,993 |
| Existing stubs | 37 |
| Stubs to generate (Phase A) | ~250 |
| Functions to promote L2 → L4 (Phase C) | ~5,500 estimated |

### Heaviest modules (signature count from .rst directives)

| Module | Signatures | Profile |
|---|---:|---|
| `os` | 309 | Phase C-1 (huge, paginate) |
| `curses` | 166 | Phase C-3 (likely defer) |
| `ssl` | 129 | Phase C-3 |
| `socket` | 112 | Phase C-3 |
| `sys` | 106 | Phase C-1 |
| `ast` | 98 | Phase C-1 |
| `typing` | 95 | Phase C-1 |
| `ctypes` | 93 | UB-7.4 (likely DENY per import-classifier) |
| `urllib.request` | 83 | Phase C-2 |
| `inspect` | 75 | Phase C-2 |
| `datetime` | 63 | Phase C-1 |

### Cost estimate

| Resource | Estimate |
|---|---|
| Wall clock (single-threaded, 10s/call × 2 retry avg) | **~33 hours** for ~5,500 LLM calls |
| LLM tokens (claude-sonnet-4.6, ~5k tokens/call avg) | **~30M tokens** |
| LLM cost (at ~$3/M input + ~$15/M output) | **~$300-500** |
| Wall clock with PYCSL_AGENT_CONCURRENCY=4 | **~8-10 hours** |
| Disk: new stubs + per-function tests + L4 index files | ~5-10 MB |

**This is the largest single agent run ever attempted in this
codebase.** Treat as a real-money real-time investment that
benefits from checkpointing.

---

## Phase A — Scaffold expansion (1 hour wall clock, ~$0)

Run `bin/generate_lib_stubs.py` to expand `src/pycsl_lib/` from
37 stubs to ~290. **No LLM calls.** No L4 promotion. Just creates
L1/L2 stubs (each function = `pass` body + `\trusted reviewer:
python-stdlib` + cite URL from the .rst source).

### Commands

```bash
# Sanity: what does generate_lib_stubs.py produce on a single test
bin/generate_lib_stubs.py argparse  # dry-run if it supports it; else expect overwrite
git diff src/pycsl_lib/argparse.py

# Full scaffold expansion
bin/generate_lib_stubs.py --all  # or whatever the bulk flag is

# Validate every new stub at least parses through pycsl --no-proof
for stub in src/pycsl_lib/*.py; do
    if ! python3 src/pycsl/pycsl.py --no-proof "$stub" > /dev/null 2>&1; then
        echo "SCAFFOLD FAIL: $stub"
    fi
done

# Regenerate the L4 Module indices for SY6-PycslLib
rm -rf projects/pycsl/BL/SY6-PycslLib/CO*
bin/cmmi-mod-index.py --system SY6-PycslLib

# Verify the audit still passes
bin/cmmi-audit.sh
```

### Acceptance criterion

- `ls src/pycsl_lib/*.py | wc -l` ≥ 280 (was 37)
- Every new stub passes `pycsl --no-proof <stub>` (parses)
- `bin/cmmi-audit.sh` exits 0 (still 8/8 gates)
- `bin/cmmi-metrics-ingest.py` snapshot shows SY6-PycslLib file
  count jumped (visible in next weekly QPM report)

### Commit point

```bash
git add src/pycsl_lib/ projects/pycsl/BL/SY6-PycslLib/
git commit -m "stdlib: scaffold ~250 new L2 stubs from test-suite/library_reference/"
```

**Why commit before Phase B**: this captures hundreds of MB-scale
new files. If Phase B/C goes sideways, you want a clean rollback
point. Profile-P single-developer CCB: commit SHA = CR-ID per
PROJECT.md.

---

## Phase B — Pilot annotation (2 hours wall clock, ~$5-10)

Run `agent-stdlib-annotate --module <name>` against a **curated
set of small, high-value modules** before unleashing `--all`. The
goal: catch agent-side bugs (prompt drift, model-version-specific
issues, runaway L3-ceiling rate) on a 20-module sample before
spending the full ~$300.

### Pilot module selection

Pick modules that:
- Are **small** (≤20 signatures from .rst count)
- Are **pure** (no I/O, no concurrency — most likely to reach L4)
- Cover **diverse semantic categories** (math, strings, data structures, etc.)

Suggested 10-module pilot:

| Module | Signatures | Why |
|---|---:|---|
| `math` | ~50 | Pure functions, mostly returns float; well-defined |
| `cmath` | ~30 | Pure complex math |
| `fractions` | ~15 | Pure value type; should L4 cleanly |
| `decimal` (small subset) | (paginate) | Tests dec-arithmetic stub coverage |
| `statistics` | ~20 | Pure aggregates over lists |
| `string` | ~10 | Constants + minimal functions |
| `keyword` | ~5 | Trivial — should be 100% L4 |
| `token` | ~10 | Constants table |
| `enum` | ~20 | Class-based; tests class-stub generation |
| `dataclasses` | ~10 | Already partly stubbed; round-trip test |

### Commands

```bash
# Run on each pilot module individually so failures are isolated
for m in math cmath fractions statistics string keyword token enum dataclasses; do
    bin/agent-stdlib-annotate --module "$m"
done

# After pilot: check L3-ceiling rate
bin/agent-stdlib-annotate --detect-gaps
cat metrics/stdlib-gap-report.json | python3 -c "
import json, sys
r = json.load(sys.stdin)
print('Total notes:', r['total_notes'])
for cat, b in r['categories'].items():
    print(f'  {cat}: {b[\"count\"]}')
"
```

### Acceptance criterion (Phase B gate)

The pilot is **green** (proceed to Phase C) when:

1. **≥7 of 10 modules** show ≥50% functions promoted L2 → L4.
2. **L3-ceiling rate is reasonable**: <30% of attempted functions
   fall back to L3-ceiling (rate above this means the agent is
   spending money without producing usable contracts).
3. **No `pycsl --proof` regressions**: every promoted module still
   exits 0.

The pilot is **red** (halt) when:

- ≥3 modules show 0 successful promotions (agent failure mode).
- L3-ceiling rate >50% (model isn't strong enough for the prompt).
- Any module's promotion broke `bin/cmmi-audit.sh`.

On red: investigate before Phase C. Likely fixes: prompt tuning in
`agent-stdlib-annotate.py`, threshold adjustment, or model change.

### Commit point

```bash
git add src/pycsl_lib/ metrics/stdlib-gap-report.json
git commit -m "stdlib: pilot — 10 small modules annotated L2→L4"
```

---

## Phase C — Bulk annotation (~10-30 hours wall clock, ~$250-500)

The main event. `agent-stdlib-annotate --all` walks every stub and
promotes L2 → L4. **This is the expensive phase.**

### Three sub-phases ranked by cost / value / risk

| Sub-phase | Scope | Wall clock | Est. cost | Risk |
|---|---|---|---|---|
| **C-1** | High-value pure modules: `math`, `cmath`, `string`, `enum`, `dataclasses`, `datetime`, `typing`, `collections`, `itertools`, `functools`, `operator`, `bisect`, `heapq`, `array`, `copy`, `pprint`, `reprlib`, `pickle`-types | 4-6 h | $80-120 | Low |
| **C-2** | Reasonably-tractable modules: `inspect`, `ast`, `re`, `json`, `csv`, `urllib.parse`, `urllib.request`, `pathlib`, `os`, `os.path`, `sys` (where possible), `hashlib`, `hmac`, `secrets`, `uuid` | 6-12 h | $100-200 | Med (some will L3-ceiling heavily) |
| **C-3** | Stretch — large/exotic modules: `socket`, `ssl`, `threading`, `multiprocessing`, `subprocess`, `asyncio`, `curses` | 4-12 h | $80-180 | High (most likely to stay at L3; could be deferred) |

### Commands

```bash
# Pre-flight: confirm current state
bin/cmmi-audit.sh && echo "audit green"

# Capture starting coverage
bin/stdlib-coverage-report.py > /tmp/coverage-pre.txt

# C-1 — high-value pure modules
for m in math cmath string enum dataclasses datetime typing \
         collections itertools functools operator bisect heapq \
         array copy pprint reprlib; do
    bin/agent-stdlib-annotate --module "$m" 2>&1 | tee -a logs/c-1-bulk.log
    # Per-module commit checkpoint
    git add -A src/pycsl_lib/"$m"* test-suite/corpus/python-reference/stdlib/"$m"/ 2>/dev/null
    git commit -m "stdlib: annotate $m (Phase C-1)" --allow-empty
done

# Mid-run: detect gaps + re-run audit
bin/agent-stdlib-annotate --detect-gaps
bin/cmmi-audit.sh
bin/stdlib-coverage-report.py > /tmp/coverage-c1.txt
diff /tmp/coverage-pre.txt /tmp/coverage-c1.txt

# C-2 — same pattern
for m in inspect ast re json csv urllib.parse urllib.request pathlib \
         os "os.path" hashlib hmac secrets uuid; do
    bin/agent-stdlib-annotate --module "$m" 2>&1 | tee -a logs/c-2-bulk.log
    git add -A src/pycsl_lib/"$(echo "$m" | tr '.' '/')"* \
            test-suite/corpus/python-reference/stdlib/"$m"/ 2>/dev/null
    git commit -m "stdlib: annotate $m (Phase C-2)" --allow-empty
done

# C-3 — stretch (only if C-1+C-2 went well)
bin/agent-stdlib-annotate --module socket
bin/agent-stdlib-annotate --module ssl
# ... etc, with per-module commits
```

### Checkpointing strategy

- **Per-module commit** (`git commit -m "stdlib: annotate <m>"`):
  cheapest rollback unit. The agent has per-module rollback
  internally; the git commit makes it an external rollback unit.
- **Every 20 modules**: run `bin/cmmi-audit.sh` + a manual diff
  review of the last batch.
- **Every 50 modules**: run `bin/agent-stdlib-annotate --detect-gaps`
  to see how categories are shaping up.

### Throttling

```bash
# Limit concurrent LLM calls (default 1)
export PYCSL_AGENT_CONCURRENCY=4    # 4× speedup; 4× peak token rate

# Hard ceiling on per-module retries
export PYCSL_AGENT_MAX_RETRIES=3

# Max wall-clock per module (kill+rollback if exceeded)
export PYCSL_AGENT_MODULE_TIMEOUT=300   # 5 minutes
```

(These env vars need to be added to `agent-stdlib-annotate.py` if
they don't exist — verify before kickoff.)

### Acceptance criterion (Phase C gate)

After Phase C completes (or you call halt):

| Metric | Threshold |
|---|---|
| Modules attempted | ≥150 (out of ~290 importable) |
| `pycsl --proof` PASS rate | ≥80% across attempted modules |
| Coverage gain (L4+%) | +5 percentage points vs Phase A baseline |
| L3-ceiling rate per category | <40% for `iterator-semantics`, `regex-semantics`, `higher-order` (these populate Phase D proposals) |
| `bin/cmmi-audit.sh` | exits 0 |
| `bin/run-reference-tests.sh` | no regression in the existing 0001+ corpus |

---

## Phase D — Gap proposals (1 hour wall clock, ~$5)

The Reconciliator step. For every category that crossed the
proposal threshold during Phase C, draft a feature plan.

### Commands

```bash
# Refresh the gap report from the post-C-bulk state
bin/agent-stdlib-annotate --detect-gaps

# For every category with count >= 5, draft a feature plan
python3 -c "
import json
r = json.load(open('metrics/stdlib-gap-report.json'))
for cat, b in r['categories'].items():
    if b['count'] >= 5 and cat != 'unclassified':
        print(cat)
" | xargs -I{} bin/agent-stdlib-annotate --propose-feature {}

ls proposed-features/missing-*-feature.md
```

### Expected output

Based on today's pre-Phase-C gap report (12 notes from 37 modules),
Phase C is likely to push at least 4 categories over threshold:

- `iterator-semantics` — likely 20-40 stuck functions after C-1
  (`itertools`, `collections`, `array`)
- `regex-semantics` — likely 30-50 after C-2 (`re`, `string`,
  `csv`, `urllib`)
- `higher-order` — likely 20-30 (`functools`, `operator`, callback
  APIs throughout)
- `io-side-effect` — likely 50+ if C-3 ran (`socket`, `ssl`,
  `subprocess`)

Each becomes a draft `proposed-features/missing-<category>-feature.md`.

### Acceptance criterion

- ≥3 draft `missing-*-feature.md` files exist in
  `proposed-features/`.
- Each draft has a populated "Stuck functions" table and an anchor
  function with citation.

### Commit point

```bash
git add proposed-features/ metrics/stdlib-gap-report.json
git commit -m "stdlib: gap proposals from Phase C — 4 categories crossed threshold"
```

---

## Phase E — Human review + supervised rollouts (open-ended)

For each draft from Phase D:

1. **Human reviews and fills design options.** The auto-drafts
   leave `## Design options` as `TODO (human)` placeholders. The
   human picks one (e.g., the iterator-semantics gap is already
   solved by `missing-iter-feature.md` — that file goes through
   the supervisor pipeline first).
2. **Move to repo root + flip STATUS: DRAFT → APPROVED.**
3. **Run the supervisor.**

```bash
# Move the first draft to repo root
mv proposed-features/missing-iter-feature.md ./missing-iter-feature.md
# (or for newly-generated drafts:)
mv proposed-features/missing-iterator-semantics-feature.md ./missing-iterator-semantics-feature.md

# Edit to STATUS: APPROVED + fill design options

# Supervised rollout (gate-only by default; halts at load-bearing files)
bin/agent-feature-supervisor --feature-file missing-iter-feature.md
```

The supervisor will halt at Phase 1 (Grammar + Module 4 changes
are load-bearing). Human implements those manually, then re-runs
the supervisor for Phases 2-3 (Module 6 emission + stdlib stub
refresh). Phase 3 will re-run `agent-stdlib-annotate` against
`itertools.py` with the new atoms, lifting all 12 iterator
functions L3 → L4.

This phase is **the long-arc engineering work** that the CMMI
framework supports but does not perform.

---

## Critical files

**Used (no rewrite):**
- `bin/generate_lib_stubs.py` — Phase A scaffolding
- `bin/agent-stdlib-annotate` — Phases B + C + D detection + D proposals
- `bin/cmmi-mod-index.py` — Phase A index regeneration
- `bin/cmmi-audit.sh` — gate after every phase
- `bin/stdlib-coverage-report.py` — coverage delta measurement
- `bin/agent-feature-supervisor` — Phase E rollouts
- `test-suite/library_reference/*.rst` — Phase A source of truth (READ-ONLY)
- `src/pycsl_lib/` — Phases A, B, C TARGET (heavy writes)
- `metrics/stdlib-gap-report.json` — Phase C+D coordination
- `proposed-features/` — Phase D OUTPUT, Phase E INPUT

**Modified by the run (NOT by this plan — by the agent during execution):**
- `src/pycsl_lib/*.py` — ~250 new files (Phase A) + heavy edits (Phase C)
- `test-suite/corpus/python-reference/stdlib/<module>/*.py` — auto-generated tests
- `projects/pycsl/BL/SY6-PycslLib/CO*/MO*/specifications/main.md` — L4 indices
- `metrics/logs/stdlib-annotator/<UTC>/*.log` — agent run logs
- `proposed-features/missing-*-feature.md` — Phase D drafts

**Possibly modified manually during Phase E:**
- `src/pycsl/Module2_Parser.py`, `src/pycsl/module6_whyml/*.py`,
  `docs/pycsl-*-reference.md`, `test-suite/annotations.md` — these
  are LOAD-BEARING; supervisor halts; human edits.

---

## Verification

After each phase:

```bash
bin/cmmi-audit.sh && \
.venv/bin/python3 -m pytest test-suite/cmmi-regression/ -q && \
bin/run-reference-tests.sh
```

Expected after each phase:

| Phase | Audit | Regression | Reference tests |
|---|---|---|---|
| A | 8/8 | 29/29 | unchanged |
| B | 8/8 | 29/29 | unchanged |
| C-1 | 8/8 | 29/29 | unchanged |
| C-2 | 8/8 | 29/29 | possibly some new XFAIL if a stub conflicts |
| C-3 | 8/8 | 29/29 | likely some new XFAIL |
| D | 8/8 | 29/29 | unchanged |

A failing reference test in C-2/C-3 is **not necessarily a stop
signal** — it likely indicates a stub got too strong a contract.
The agent's per-module rollback should catch most of these. If
not, manually revert the offending module.

---

## Rollback strategy

The agent has per-module rollback built in. External rollback
units (this plan's choice) are the **per-module commits** in
Phase C. To revert one module:

```bash
git revert <commit-sha-for-that-module>
```

To roll back a whole sub-phase:

```bash
git revert <sub-phase-start-commit>..HEAD
```

Worst case (full Phase C rollback):

```bash
git revert <phase-c-1-start>..HEAD
# OR (more destructive but cleaner):
git reset --hard <pre-phase-A-commit>   # ← NEVER WITHOUT EXPLICIT AUTH
```

The `git reset --hard` option is listed but **forbidden by the
supervisor's `_git()` wrapper**; do it manually only if you've
backed up the staged work.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| LLM cost runaway ($500+) | Per-module commits + Phase B canary; halt if pilot is red |
| `bin/cmmi-audit.sh` breaks mid-Phase-C | Per-module commits → cheap to revert one offender |
| Agent produces semantically-wrong contracts | `pycsl --proof` rejects them; gate fails; per-module rollback engages |
| L3-ceiling rate explodes | Phase B pilot catches this before Phase C money is spent |
| Phase C produces too many test files (disk pressure) | `--no-tests` flag if it exists, or filter post-hoc |
| Model unavailable / API outage | Cron retry; or pause and resume from cursor |
| Concurrency races (PYCSL_AGENT_CONCURRENCY > 1) | File-level locking in `_apply_or_rollback`; verify before raising the limit |
| Stub conflicts with existing self-annotation suite | `bin/self-annotate-mirror-check.sh` catches drift; re-run mirror gen after Phase C |
| Two-sided spec-mirror drift (PROJECT.md still says 40 files but src/pycsl_lib has 290) | `bin/cmmi-metrics-ingest.py` snapshot makes drift visible in next QPM report |

---

## What this plan does NOT do

- **Does not annotate the C-extension modules** on the deny-list
  (`ctypes`, `cffi`, `numpy.ctypeslib`, etc. per UB-7.4). Phase A
  skips them; Phase C explicitly avoids them.
- **Does not modify `Module2_Parser.py` / `module6_whyml/*` / 3
  normative reference docs** — those are load-bearing per
  `config/skills/agent-stdlib-annotate/references/load-bearing-files.md`.
  Phase E delegates those edits to the human.
- **Does not commit to landing all of Phase C.** Each sub-phase
  (C-1, C-2, C-3) is independently shippable. If C-1 succeeds and
  C-2 is too expensive, stop at C-1.
- **Does not auto-approve `proposed-features/` drafts.** The
  human always reviews + fills design options before the
  supervisor runs.
- **Does not promise 100% L4+ coverage.** The realistic ceiling
  given today's contract surface is probably ~60% (the rest are
  iterator-semantics, regex-semantics, higher-order, etc., which
  need Phase E feature work first).
- **Does not start without explicit "go" from the user.** This
  plan is `STATUS: DRAFT`. Flip to `APPROVED` before kickoff.

---

## Calendar-gated transitions

| Trigger | Action |
|---|---|
| `bin/cmmi-weekly-snapshot.sh` runs at week 8 | Auto-flip QPM band weak → preliminary. Stdlib-coverage trend now reportable in `qpm-report-N.md`. |
| `bin/cmmi-queue-coverage-diff.py` reports SAFE for 30 days | Item 3.5x decommission unblocked (separate authorisation). |
| ≥1 Phase E feature lands end-to-end | Item 3.4r — delete `metrics/logs/` fallback in `_read_agent_log_context`. |

The stdlib annotation run accelerates all three by generating
real bridge traffic, real KPI data, and (via Phase E) real
supervisor exercise.

---

## Suggested first commit (today, low-risk start)

If "launch today" means **start Phase A today**, the smallest
useful first commit is:

```bash
# 30 minutes
bin/generate_lib_stubs.py --dry-run  # if supported; else read source
# inspect what it would produce against test-suite/library_reference/

# Actually scaffold (cheap, no LLM)
bin/generate_lib_stubs.py --all

# Validate parse
bin/cmmi-audit.sh

# Regenerate indices
rm -rf projects/pycsl/BL/SY6-PycslLib/CO*
bin/cmmi-mod-index.py --system SY6-PycslLib

# Commit Phase A
git add src/pycsl_lib/ projects/pycsl/BL/SY6-PycslLib/
git commit -m "$(cat <<'EOF'
stdlib: scaffold L2 stubs for ~250 stdlib modules

Expands src/pycsl_lib/ from 37 to ~290 stubs using
bin/generate_lib_stubs.py against test-suite/library_reference/
(331 .rst files, 5993 parseable signatures).

Each new stub carries:
  - Function/class signatures derived from .rst directives
  - \trusted reviewer: python-stdlib annotation
  - cite: URL to docs.python.org

L4 promotion deferred to Phase C of full-stdlib-plan.md.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

Then **pause for review** before Phase B. Phase A is reversible
in one `git revert`. Phases B/C/D each spend real LLM money;
gate each on the previous one's acceptance criterion.

---

## References

- [`docs/cmmi-for-humans.md`](docs/cmmi-for-humans.md) Part 6 — the
  agent pipeline (detect → propose → supervise) this plan exercises
  end-to-end.
- [`docs/self-annotation-status.md`](docs/self-annotation-status.md)
  — current Squeeze S4 status (suite of 26 modules, 1
  body-verified) which Phase C strengthens (S8 = real-world test
  cases).
- [`config/skills/csl-from-scratch/SKILL.md`](config/skills/csl-from-scratch/SKILL.md)
  §0.5 — the Squeeze Strategy that defines S1 (CSL contracts) +
  S8 (real-world test cases) — both owned by SY6-PycslLib per
  PROJECT.md.
- [`config/skills/pycsl-stdlib-coverage/SKILL.md`](config/skills/pycsl-stdlib-coverage/SKILL.md)
  §9 — the three-artefact discipline (calls-english.md,
  calls-pycsl.md, src/pycsl_lib/) Phase A keeps in lockstep.
- [`better-agent.md`](better-agent.md) — the Reconciliator design
  Phase D + E exercise.
- [`missing-iter-feature.md`](missing-iter-feature.md) — the
  canonical worked example Phase E will drive end-to-end first.
- `bin/generate_lib_stubs.py` — the existing scaffolder (Phase A).
- `bin/agent-stdlib-annotate` — the existing promoter (Phases B + C + D).
- `bin/agent-feature-supervisor` — the existing Reconciliator
  (Phase E).
- `test-suite/library_reference/*.rst` — the source of truth.
- `projects/pycsl/PROJECT.md` — SY6-PycslLib ownership block.
