---
name: self-tcb-reduction-driver
description: >-
  Drives (monitors) the self-tcb-reduction Squeeze Loop: when the base loop hits a WALL
  (a `\trusted` stub it cannot convert and that is not a cheap win), this meta-loop runs
  the review-and-break workflow — write a self-contained state-of-the-art report `XXX.md`,
  get an INDEPENDENT `XXX-response.md` from a fable reviewer that never sees the sub-loop's
  contents, synthesize `XXX-impl.md`, then execute it spike-gated with every agent claim
  verified against the base loop's three L-planes. It is an SL monitoring an SL (per
  sl-monitoring-sl). Use when the user says "run the self-tcb-reduction driver", "drive the
  tcb reduction", "automate breaking the walls", "monitor self-tcb-reduction", or asks to
  break a named wall XXX end-to-end. Add a DURATION ("... for 2 hours", "... for 90 min")
  to run AUTONOMOUS time-boxed mode — iterate walls back-to-back with NO per-iteration
  prompting until the wall-clock deadline, committing each increment (see §A). Companion:
  self-tcb-reduction (the base loop), sl-monitoring-sl (the meta-pattern), sl-builder.
---

# self-tcb-reduction-driver — a squeeze loop that drives the self-tcb-reduction squeeze loop

This meta-loop watches the **base loop** (`self-tcb-reduction`, which converts the emitter
mirror's `\trusted` stubs to verified bodies) and, when the base loop hits a **wall** —
a stub it cannot convert with its normal recognizers and that measurement shows is not a
cheap win — runs the **wall-breaking workflow** end-to-end. It is a *monitor of a monitor*
(`sl-monitoring-sl`): the driver squeezes the wall — a *soft, sub-loop-authored claim that
"X cannot be done"* — against the base loop's own bounds, from an evidence base the
sub-loop's actors do not share. The workflow it automates is exactly the one run manually
and validated on the `_field_type_of` wall (report → independent review → impl plan →
spike-gated execute → conversion OR sanctioned refutation).

## A. Modes — interactive vs AUTONOMOUS time-boxed

- **Interactive (no duration).** "Run the self-tcb-reduction-driver SL loop" → run ONE driver iteration
  (§4), present the outcome, and STOP (the user drives the cadence — as runs #1/#2 did). Gate W may
  present its escalate/decline decision.
- **Autonomous time-boxed (a duration is given).** "... **for 2 hours**" / "... **for 90 min**" / "...
  **for 45m**" → iterate walls **back-to-back with NO per-iteration prompting** until a wall-clock
  deadline. This is the mode this section governs.

### A.1 Setup (once, at invocation)
1. Parse the duration to seconds. Compute the deadline and PERSIST it to a file (so it survives context
   summarization across a long run — do NOT hold it only in context):
   ```bash
   SECS=7200   # 2h; 90 min -> 5400; 45m -> 2700
   date -d "+${SECS} seconds" +%s > getting-better/.driver-deadline
   date +%s > getting-better/.driver-started
   ```
2. Announce: "Autonomous driver: running until <deadline>. Iterating walls; committing each increment; no
   prompts until the deadline or you interrupt."

### A.2 The autonomous loop (repeat until the deadline)
Each iteration, in order, WITHOUT asking the user:
1. **Clock check.** `NOW=$(date +%s); DL=$(cat getting-better/.driver-deadline)`. If `NOW >= DL` → go to A.3
   (finish). Reserve headroom: if `DL - NOW` is less than the estimated cost of the next step (a full cycle
   needs ~1 fable review + spike; an inline conversion needs ~1 gate battery), do only what fits — prefer a
   cheap inline conversion or a measurement over starting a full cycle that can't finish before the deadline.
2. **Run the base loop as a SUB-AGENT, NON-INTERACTIVELY.** It must NOT present its §11 menu; it does its
   measure-before-build triage and RETURNS the structured wall-signal `{stub, attempts, first_blocker,
   cheap_win}` (Gate W's input) — never its rationale (the barrier).
3. **Gate W** (autonomous): `cheap_win == true` → the base loop converts it inline (full base-loop gate
   battery via the driver-verifier), commit, next iteration. `cheap_win == false` AND stuck AND not already
   CERTIFIED-BOUNDARY → escalate the full cycle (§4 steps 3–8: report → fable review [Gate R] → impl plan
   [Gate P] → spike [Gate S] → BROKEN build [Gate B/C] or CERTIFIED-BOUNDARY). Neither → record and skip.
4. **Commit EVERY increment immediately** (a conversion, a CERTIFIED-BOUNDARY record, a lesson) so an
   interruption at any point loses nothing. NEVER leave a dirty tree between iterations; revert a
   sprawling/refuted build to clean before committing its finding.
5. **Gate S-lesson** on any consolidated lesson → `wall-lessons.md`. Next iteration.

### A.3 Finish (deadline reached, or the frontier is at floor)
- Stop iterating. `rm getting-better/.driver-deadline getting-better/.driver-started`.
- Emit ONE summary: walls RESOLVED this run (BROKEN vs CERTIFIED-BOUNDARY), conversions + count delta,
  lessons banked, and the unpushed-commit count. Do NOT auto-push (the standing rule holds: push only on
  an explicit "push"/"push it") — list what is ready to push.
- If the frontier reaches its floor (every remaining stub is BROKEN / CERTIFIED-BOUNDARY / below Gate W)
  BEFORE the deadline, STOP EARLY and say so — do not spin on non-walls to burn the clock.

### A.4 Autonomy discipline (non-negotiable — speed never relaxes rigor)
- **The gate battery is unchanged.** Autonomous mode runs FASTER by not prompting, never by skipping a
  gate: fidelity ∧ whole-file Why3 ∧ byte-diff-0 (or sanctioned reset) ∧ ledger==3 ∧ non-vacuity, and every
  agent claim re-verified by the driver-verifier (§2). A speed-motivated `--fun`-only accept is forbidden.
- **Cross-turn continuation.** A single turn's context is finite; when it fills before the deadline, the
  harness summarizes and continues — the persisted `.driver-deadline` file is how the next context window
  knows to keep going and when to stop (re-read it each iteration; do not re-ask the user). If the harness
  offers `ScheduleWakeup`/`/loop` dynamic pacing, a long idle wait (e.g. a background proof) may reschedule
  rather than block, but the deadline file remains the single source of truth.
- **Interruptibility.** A user message mid-run is honored immediately (answer it, then resume or stop per
  their instruction). Each increment being committed means an interrupt is always at a clean boundary.
- **Escalate-not-thrash, time-aware.** A per-wall attempt budget still applies; additionally, do not START
  a full cycle whose fable-review + spike cannot plausibly finish before the deadline — defer it (record
  the wall-signal for the next run) and spend the tail on cheaper items.

## 0. Deliverable & correctness

- **Deliverable (per wall XXX):** the wall is **RESOLVED** — one of two gate-defined verdicts,
  never a third:
  - **BROKEN** — one or more `\trusted` stubs behind the wall convert to verified bodies,
    each passing the base loop's full gate battery (fidelity ∧ Why3 ∧ byte-diff-0), `\trusted`
    count strictly down, ledger unchanged.
  - **CERTIFIED-BOUNDARY (leave-trusted)** — the wall is a genuine limit, proven by the impl
    plan's make-or-break spike REFUTING the build (before any emitter work), recorded with a
    reproducible reason (a hand `.mlw`, an oracle run) and a one-line lesson.
- **"Correct" (checkable):** the report `XXX.md` states nothing `L` refutes; the reviewer's
  `XXX-response.md` is authored WITHOUT the sub-loop's rationale in context; `XXX-impl.md`'s
  first action is a make-or-break spike (measure-before-build); every executing agent's claim
  is re-verified by the driver against the three L-planes; the final verdict is BROKEN (gates
  green) or CERTIFIED-BOUNDARY (spike refuted) — never "grind until done".
- **Terrain: B (authored authority) + C (split planes).** The wall report is `U` authored
  upstream (by the sub-loop) and independently reviewed; correctness splits across the base
  loop's three disjoint oracle planes that must never blend.
- **Dominant coherent-and-wrong to guard:** (1) a **wrong report** the reviewer rubber-stamps
  (mitigated: reviewer gets `L`, not just prose); (2) a **wrong/incomplete impl plan** executed
  to sprawl (mitigated: spike-gate + refutation exit); (3) an **agent over-claim** accepted
  (mitigated: three-L-plane re-verification); (4) an **over-general wall-lesson** entering the
  store (mitigated: Gate S); (5) **escalating a non-wall** (mitigated: the wall-escalation gate).

## 1. Bounds

- **Upper bound `U`:** the base loop's contract discipline (`self-tcb-reduction.md`,
  `triage-ranked-tcb.md`, §10 lessons: type-safety+frame contract shape; measure-before-build;
  no-unused-facade; coupling rule; ledger stays 3) **+** the wall report `XXX.md` (a *soft*
  reading the reviewer may refute or carve). The strongest claim any driver actor may make.
- **Lower bound `L` (the base loop's three disjoint executable planes, ALL required):**
  - **Fidelity:** `bin/check-self-annotate-sync.sh` ∧ `bin/self-annotate-mirror-check.sh`.
  - **Type-safety:** `python3 src/pycsl/pycsl.py <file> --import-path src/pycsl` (whole-file
    proof, §10.10) + `--fun` per method; `proof_axiom_allowlist` unchanged.
  - **Corpus inertness / sanctioned reset:** `bin/byte-diff-sweep.sh` + `diff -rq` vs a
    worktree-at-HEAD baseline == 0 — OR, for a semantics-preserving shared-theory change, the
    diff is *exactly* the change AND every affected program re-proves (the M1 discipline).
  Plus the ledger audit (`Print Assumptions` / `#print axioms` == 3) and the strictly-decreasing
  `\trusted` `wc -l`.

## 2. Actors and their disjoint (U,L) pairs

| Actor | Builds | U (above) | L (below) | Forbidden move | Must NOT see |
|-------|--------|-----------|-----------|----------------|--------------|
| **driver-coordinator** | wall detection, phase sequencing, verdict (BROKEN / CERTIFIED-BOUNDARY), the wall-lesson ledger | base loop `U` + the report | the gate-machine outputs + spike verdicts | edit the emitter/mirror; rubber-stamp a claim or a lesson | the base loop's in-context rationale (runs it as a **sub-agent**) |
| **base loop** (`self-tcb-reduction`, run as a SUB-AGENT) | the routine conversions; surfaces a wall when stuck | base loop `U` | base loop `L` (its three planes) | (its own §2 forbidden moves) | — |
| **report author** (may be the driver, tainted) | `XXX.md` — the state-of-the-art wall statement | base loop `U` | — (this is `U`, not `L`) | claim more than the measured facts | — |
| **fable reviewer** (independent, `subagent_type` fable) | `XXX-response.md` | base loop `U` (the discipline) | base loop `L` (Why3/byte-diff/**can spike**) | see the sub-loop's rationale, attempts, or reasoning; edit source | **the sub-loop's contents** (only `XXX.md` + `L` in context) |
| **impl planner** | `XXX-impl.md` (spike-first, refutation-exit) | `XXX.md` ∧ `XXX-response.md` | — | assert "cleared" without a spike | — |
| **executor agent(s)** | the emitter/mirror edits per `XXX-impl.md` | the impl plan + the fixed contract shape | Why3 **type-check** (`--fun`) locally | weaken/vacuate a contract; add an axiom; loosen a gate; leave an un-trusted-unverified method | the byte-diff baseline; the driver's verdict logic |
| **driver-verifier** | re-runs the three L-planes FRESH on every executor claim; the spike re-proof | the plan's gate battery + the contract shape | the actual oracle verdicts | trust an agent's self-reported gate result | the executor's recognizer rationale (surface + gate results only) |

- **Disjointness (C1):** the **fable reviewer** holds `U`+`L` but NEVER the sub-loop's rationale
  (its whole value is the independent evidence base); the **report author** holds only `U` (it may
  be tainted — that is *why* the reviewer exists); the **executor** holds the plan + local
  type-check but never the corpus baseline or the verdict; the **driver-verifier** holds the
  acceptance oracles but never the executor's code rationale. No actor can relieve its own
  constraint.
- **Catchability (C2):** report author's *coherent-and-wrong wall claim* → caught by the fable
  reviewer (independent `U`+`L`); reviewer's *over-scoped fix* → caught by the impl plan's
  make-or-break spike (measure); executor's *over-claim / sprawl* → caught by the driver-verifier's
  three-L-planes + the refutation exit; driver's *over-general lesson* → caught by Gate S.

## 3. Gates

- **Gate W (wall-escalation — fires the whole workflow, or does NOT).** The base-loop sub-agent
  RETURNS, as its soft output (never its in-context rationale — the barrier), a structured
  **wall-signal**: `{stub, attempts_spent, first_blocker (the exact --fun/type error), cheap_win:
  bool}` where `cheap_win` is the base loop's own measure-before-build verdict (port → whole-body
  `--fun` → classify → revert). Escalate to the report→review→impl→execute cycle ONLY if
  `attempts_spent ≥ the per-stub budget` AND `cheap_win == false` AND the stub is not already in
  `wall-lessons.md` as CERTIFIED-BOUNDARY. Otherwise the base loop handles it inline. The driver
  gates on the RETURNED wall-signal, not by reading the sub-loop's work — this is the cost control
  (the cycle is expensive: report + fable + impl + multi-agent execute) AND the barrier (the driver
  decides from soft outputs only).
- **Gate R (reviewer independence — WITH ARTIFACT TEETH).** `XXX-response.md` is accepted only if
  BOTH hold: (a) it was authored by an actor whose context contained `XXX.md` + `L` and provably
  NOT the sub-loop's rationale (enforced by spawning fable with only the report + repo/oracle
  access, never the base-loop transcript); AND (b) **it contains at least one independent ORACLE
  ARTIFACT** — a hand `.mlw` the reviewer wrote and proved with `why3 prove`, a `byte-diff-sweep`
  it ran, an emit-and-`grep` of the actual generated WhyML, or a `pycsl --fun` run — that CONFIRMS
  or REFUTES a NAMED factual claim of `XXX.md` (e.g. "the report says `map` can't be iterated —
  verified: `for x in m` is a why3 syntax error", or "the report says byte-inert — refuted: 0882
  changed"). A response that only re-reasons from the prose, with **zero** oracle runs cited, is
  REJECTED as a rubber stamp — the fable prompt (step 4) MUST demand the artifact, and the driver
  MUST check the response cites one. This is the load-bearing fix: the reviewer's value is a
  *different evidence base (`L`)*, not a second opinion on the prose; an unrun `L` makes the review
  a `U`-only audit that must SAY SO and is downgraded (per sl-monitoring-sl "oracle availability is
  honest, not assumed").
- **Gate P (impl-plan acceptance — the spike-gate cannot be skipped).** `XXX-impl.md` is accepted
  for execution ONLY if its FIRST action is a named **make-or-break falsifier spike** (a cheapest
  test that could REFUTE the whole build before any emitter edit) AND it carries an explicit
  **refutation exit** (a "spike REFUTES → CERTIFIED-BOUNDARY, stop" branch) AND the three-L-plane
  gate battery AND honest costed scope. An impl plan that begins with "build" instead of "spike",
  or that has no refutation branch, is REJECTED and re-planned — this is what prevents step 6's
  "execute until done" from grinding an impossible wall (the failure point of the raw idea).
- **Gate S (impl-plan spike — measure before build).** `XXX-impl.md`'s FIRST executed action is
  its make-or-break spike. Its verdict routes the loop: spike PASSES → proceed to the build; spike
  REFUTES → the wall is CERTIFIED-BOUNDARY (record + stop, do NOT build); spike REFINES (a
  different blocker) → re-plan the residual, do not sprawl. "Cleared" is never asserted without the
  spike's run.
- **Gate B (machine — per executor increment).** All three L-planes pass FRESH (driver-verifier,
  not the executor's self-report): fidelity ∧ whole-file Why3 ∧ byte-diff-0 (or sanctioned-reset
  + re-proof) ∧ ledger==3 ∧ `\trusted` strictly down ∧ nothing smuggled (no axiom, no gate
  loosening, no un-trusted-unverified method).
- **Gate C (coverage / no-blend / coherent-and-wrong).** The three planes never blend (a `--fun`
  pass never stands in for the whole-file proof; neither stands in for byte-diff-0 or fidelity);
  non-vacuity (the converted body reads real accessors, no opaque `_get_N <hash>`); a
  feature-editing-a-verified-emitter-method carries the §10.4 re-port + re-proof in the SAME
  increment; every touched stub ends VERIFIED or FLOOR+reason.
- **Gate S-lesson (skill-consistency, per sl-monitoring-sl) — WITH A CONCRETE STORE.** The lesson
  **store** is a named ledger: `getting-better/wall-lessons.md` (one entry per resolved wall), and,
  for a lesson general enough to change base-loop policy, a CARVE-OUT appended to
  `self-tcb-reduction.md` §10 — NEVER an inline edit to the base loop's reasoning. The **write
  protocol:** a candidate lesson (the driver's compressed takeaway from a resolved wall, e.g.
  "search-by-value-field ≠ enumerate → check for a missing index before `pydict`") is checked
  BEFORE it is written: **ignore-signal** lessons ("treat X as a wall/noise") get the **trigger
  test** (perturb X, does `L`'s verdict move?) → PASS / CARVE-OUT / REJECT; **defer-to-oracle**
  lessons ("on case S do the L-sanctioned action") get the **validity test** (does `L` actually
  distinguish S?). Only PASS or CARVE-OUT is written, WITH: the wall it came from, the `L`-input
  that revealed the divergence, and (for a carve-out) the exact narrower rule. An over-general
  lesson is carved to its valid complement, never kept whole; an irreconcilable one is REJECTED and
  logged (loud-fail). This is the gate that stops "all `.values()` are walls" from entering as a
  rule — the trigger test finds the reverse-index-fixable input and forces the carve-out.

## 4. Loop steps (per wall XXX)

1. **driver-coordinator** runs `self-tcb-reduction` as a **sub-agent** (one level deeper — the
   barrier is physical). The sub-agent does routine conversions and, on a stuck stub, returns a
   wall signal (the stub, its measured first blocker) — NOT its full rationale.
2. **Gate W** → escalate or continue. On escalate, the driver names the wall `XXX` (a short slug).
3. **report author** writes the self-contained state-of-the-art report:
   > *"Write the self-contained report `XXX.md` to be sent for review regarding state of the art.
   > Provide the global picture to help the reviewer."*
   It states the global picture (what PyCSL is, where the wall sits), the wall as first seen, the
   deeper truth (is it fundamental or a modeling choice?), the SOTA lens, the honestly-costed routes,
   and honest limits — every claim reproducible from cited evidence.
4. **fable reviewer** (Gate R): spawn a **fable** sub-agent (`model: fable` / `subagent_type` fable)
   whose context is `XXX.md` + repo access to the base loop `U`/`L` (Why3, byte-diff, `pycsl --fun`,
   the ability to write+prove a `.mlw` spike) and **NOT** the sub-loop's contents/transcript. Prompt:
   *"Using `XXX.md`, generate `XXX-response.md` — an independent review. You MUST RUN the oracle:
   write and prove at least one `.mlw` spike, or run a byte-diff / emit-and-grep / `pycsl --fun`, to
   CONFIRM or REFUTE a named factual claim of the report — cite the run and its output. A review with
   no oracle run is not acceptable."* Gate R checks the returned `XXX-response.md` cites ≥1 oracle
   artifact; if not, REJECT and re-spawn (a prose-only response is the rubber stamp this gate exists
   to stop).
5. **impl planner** synthesizes:
   > *"Using `XXX-response.md` and `XXX.md`, generate `XXX-impl.md`, an implementation plan to break
   > the wall."*
   Then **Gate P**: accept the plan for execution ONLY if its first action is a make-or-break spike
   with a refutation exit + the three-L-plane battery + costed scope; else re-plan (no execution from
   a build-first plan).
6. **executor(s)** (spawned per the plan): *"Execute `XXX-impl.md` by spawning one or several agents
   to do the plan. Favor rigor. Check the claims made by the agent."* Each agent leaves edits for the
   driver-verifier — no commit.
7. **Gate S (spike)** → PASS (build) / REFUTE (CERTIFIED-BOUNDARY, record + stop) / REFINE (re-plan
   residual). Then per built increment: **Gate B** (three L-planes FRESH, driver-verifier) → **Gate C**
   (no-blend + non-vacuity + §10.4). Verify EVERY agent claim independently — this session's record
   shows agents over-claim on `--fun`-only, on `ugrep` counts, on "byte-inert" premises.
8. **Verdict.** BROKEN (commit the conversions, `\trusted` down) or CERTIFIED-BOUNDARY (commit the
   report+response+impl+spike evidence, `\trusted` unchanged, wall recorded). **Gate S-lesson** on any
   consolidated lesson. Next wall. **Never** a partial/un-verified commit; **never** "grind until done".

## 5. Executable oracle setup

"A verdict" = the conjunction of §1's three L planes + ledger==3 + strictly-decreasing `\trusted`.
Per-increment (driver-verifier, FRESH from the surface):
```bash
bash bin/check-self-annotate-sync.sh && bash bin/self-annotate-mirror-check.sh          # fidelity
PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <file> --import-path src/pycsl               # whole-file proof
# byte-diff-0 (worktree-at-HEAD baseline, .venv symlinked, ONE foreground sweep):
git worktree add --detach <wt> HEAD; ( cd <wt> && bin/byte-diff-sweep.sh /tmp/before )
bin/byte-diff-sweep.sh /tmp/after && diff -rq /tmp/before /tmp/after                     # inertness (or sanctioned reset)
for f in $(find src/self-annotate/src -name '*.py'); do grep -cF '\trusted' "$f"; done | paste -sd+ | bc  # count (grep -F: avoid ugrep \t quirk)
```
The **spike** oracle (Gate S) is a hand-written `.mlw` proven with `why3 prove -P alt-ergo` (fall back
to `-P z3`), asserting the impl plan's make-or-break target is reachable/provable/ledger-clean — run,
not argued (`getting-better/composition-wall/*.mlw` are the templates).

## 6. Done criteria (gate-defined, never self-declared)

A wall is RESOLVED when the driver-verifier's gates return BROKEN (all three L-planes green on the
conversion, ledger 3, count down) OR CERTIFIED-BOUNDARY (the impl plan's spike REFUTED the build with a
reproducible reason). The campaign is at floor when every remaining stub is BROKEN, CERTIFIED-BOUNDARY,
or below Gate W (a cheap win the base loop handles). No actor's self-report counts.

## 7. Stabilizers engaged (collapse-mode defenses)

- **Rubber-stamped wrong report** → Gate R (reviewer gets `L`, not just prose; independence enforced by
  the fable barrier) + the impl-plan spike (an independent `L`-run that a prose-only review can't fake).
- **Grind-until-done on an impossible wall** → the refutation exit: "done" = BROKEN ∨ CERTIFIED-BOUNDARY,
  the impl plan is spike-first, a REFUTE verdict stops the build.
- **Agent over-claim accepted** → the three-L-plane driver-verifier; the executor never owns a gate
  verdict; count via `grep -F` (the `ugrep \t` trap).
- **Over-general wall-lesson** → Gate S-lesson (trigger/validity test → carve-out, never keep-whole).
- **Escalating a non-wall (cost blowout)** → Gate W (only genuine, measured, non-cheap walls escalate).
- **Barrier leak (driver sees sub-loop rationale)** → run `self-tcb-reduction` as a SUB-AGENT; run the
  reviewer as a fable sub-agent with only `XXX.md`+`L`; both barriers are physical (context), not honorary.
- **Feature edits a verified emitter method** → Gate C's §10.4 re-port + re-proof in the same increment.
- **Sanctioned-but-unproven shared-theory change** → the M1 discipline (diff = exactly-the-change ∧ all
  affected programs re-prove ∧ ledger 3), never "byte-diff nonzero, probably fine".

## 8. Execution order

Run the base-loop sub-agent → Gate W → (on a wall) report → fable review (Gate R) → impl plan → spike
(Gate S) → BROKEN build (Gate B/C) or CERTIFIED-BOUNDARY. Sequence walls serially (shared emitter
recognizers ⇒ conflicts); the ONLY safely-parallel actor is the read-only measurement/triage probe.
Escalate-not-thrash: a per-wall attempt budget; a refuted or sprawling build reverts to clean + records
a gap, never leaves an un-verified tree.

## 9. Reference: the workflow's proven instance

The `_field_type_of` wall is the worked example this loop generalizes: `file-type-of-wall.md` (report,
SOTA framing: map-non-enumerability is a representation choice, not fundamental), `…-response.md` (the
independent fable review's reverse-index carve-out), `…-impl.md` (the spike-gated plan), and the outcome
(S-R2 spike REFUTED the map-`.values()` build → CERTIFIED-BOUNDARY; the reverse-index+U path validated its
mechanism but cascaded → residuals scoped). It demonstrates all four gate verdicts: Gate R caught the
report's over-scope, Gate S refuted one build and refined another, Gate B/C caught agent over-claims, and
the Gate S-lesson carve-out ("search-by-value-field ≠ enumerate") repaired an over-general wall-lesson.
