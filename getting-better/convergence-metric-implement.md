# Implementation plan — convergence metrics for campaign #49

Companion to `ideas-for-convergence-metric.md` (2026-09-13). That document proposes the
metrics; this one says what to build, in what order, what counts as done, and what each step
can get wrong. Written 2026-09-13 at HEAD `ed5bd036`, window #6 (deadline Thu Sep 17 09:08:45
UTC), gen #16 live.

**Read the review in §0 before implementing §3.5 — one headline number in the source report is
computed from a premise the campaign's own rules forbid, and it should not be published until
it is recomputed.**

---

## 0. Review of the source report

### What it got right, and should be kept verbatim

* **Splitting the question.** "Is the hunt converging?" and "when can marker reduction resume?"
  need different instruments, and (b) is **not** gated on (a). The backlog has said since
  2026-09-02 that (b) is gated on *building a named capability*. Nothing in the hunt's state
  is a reason to keep (b) frozen.
* **§3.3 capture–recapture.** The only proposal that estimates the population *not yet found*.
  Everything else counts what was found. This is the actual answer to the user's question.
* **§3.6 assumption-honesty deficit.** The standout practical find: *"reduces the amount that
  is trusted without reducing the count that is trusted."* 70 silent-raise stubs, already
  ratcheted, needing no capability. This is the only trust-reduction move available today.
* **§0.5 — no hunter-independent instrument.** 0 of 56 routes were discovered by a plane,
  ratchet, or differential corpus going red. Every one came from the driver probing. That is
  the deepest finding in the report and it reframes the whole question: convergence cannot be
  *measured* by an instrument that only ever confirms what the hunter already decided to look at.
* **Every number carries the command that produced it.** The campaign's own discipline applied
  to its own meta-level. Keep this requirement for every metric added below.

### Three challenges — act on these

**(1) §3.5's `914 / 3236 = 28.2 %` is not measured, it is inferred, and the inference is the
exact error class this campaign keeps finding in its own code.**

The report computes verified defs as `mirror defs − markers` = `1373 − 459 = 914`. That treats
*absence of a `\trusted` marker* as *evidence of proof*. It is not. An unmarked mirror def is
verified only if its file's whole-file proof actually ran and returned rc=0 with zero non-Valid
goals. A file never proved, or proved with timeouts, contributes unmarked defs that nobody has
verified — and they would be counted as verified here.

This is structurally identical to route #94 (*a guard whose population is empty has checked
nothing and looks exactly like a guard that passed*) and to the campaign's vacuity rule. **Do
not publish 28.2 % until it is recomputed from proof verdicts.** See Phase 2, step 2.2 — the
per-file `.rc` evidence already exists under `getting-better/proofs49/`.

Expect the corrected number to be **lower**, possibly much lower, because it will exclude every
mirror file with no recent whole-file proof on record.

**(2) §3.3's independence assumption is weaker than stated, and the bias runs the dangerous
way.** Two agents reading the same emitter with the same skill share a *method*, so their
findings overlap more than two independent samplers would. In Lincoln–Petersen, excess overlap
inflates `m`, which deflates `N̂ = n₁·n₂/m` — i.e. it systematically **under**-estimates what
remains, and reports "nearly done" too early. For a soundness campaign that is the wrong
direction to be wrong in.

The report files this under "cannot see". Promote it to a usage rule: **treat `N̂ − known` as a
lower bound on what remains, never as an estimate of completion.** A high `m/n₂` is weak
evidence of convergence; a low `m/n₂` is strong evidence *against* it. The asymmetry is the
point, and it is still worth running for the second reading alone.

**(3) §3.8's byte-inertness is asserted, not measured.** Adding a `reason:` token to all 459
marker lines is a 459-line mirror edit. The report says it "should be" byte-inert because the
marker is a comment to Module 2. *"Should be"* is precisely the claim this campaign punishes —
see #96's `\trusted` val silently dropping an `assigns`, where a comment-level construct turned
out to change emission. **Pilot on one file, run the emission diff, and only then touch the
other 458.** Encoded as a hard gate in Phase 3.

### Ordering disagreement, stated and then deferred

The report's week plan puts bookkeeping (ledger, histogram) first and the two
hunter-independent instruments (§3.3 blind window, §3.4 generated sampler) at positions 4 and
5. Given that the report's own deepest finding is *the campaign has no hunter-independent
instrument*, that ordering treats the symptom before the disease.

I am keeping the report's order anyway, for one reason: the bookkeeping is ~3 hours total and
the sampler is 1–2 days, and the bookkeeping is what makes the sampler's result *interpretable*
when it lands (without a denominator you cannot compare the blind hunter's yield to the
driver's). But Phase 4 should not slip. If a generation has to choose, **run the blind window
before building the generated sampler** — one agent-window buys the first real population
signal; the sampler is the standing instrument that replaces it.

---

## 1. Phasing overview

| phase | deliverable | cost | prover time | blocks on |
|---|---|---|---|---|
| 1 | probe ledger `probes.tsv` + driver rule | ~1 h | none | — |
| 2 | corrected verified-fraction + `--metrics` output | ~3 h | none (reads existing `.rc`) | — |
| 3 | marker reason taxonomy | ~3 h + pilot | emission diff only | 2 |
| 4 | silent-raise burn-down 70 → 0 | ~70 edits, batched | mirror re-proofs | 3 (taxonomy tags the stubs) |
| 5 | blind recapture window | 1 agent window | yes — needs a quiet box | 1 (needs the denominator) |
| 6 | generated differential sampler | 1–2 days | yes — 200 files/run | 5 |

Phases 1–3 are pure bookkeeping and can run **alongside** a live driver generation. Phases 4–6
consume the box and must respect the campaign's standing constraint: **~4 whole-file proofs
concurrently, never alongside the reference suite** (the `statements.py` mirror alone took
88 minutes on 2026-09-13).

---

## 2. Phase-by-phase

### Phase 1 — probe ledger (the denominator)

**Build.** `getting-better/open-routes/probes.tsv`, one row per probe, appended by the driver:

```
date	gen	generator	candidate	verdict	route	order	note
2026-09-13	16	continue-census	_collect_protect_index_sites	LIVE	97	1	base class w/o fields
2026-09-13	16	continue-census	liskov-name-miss	FAIL-CLOSED	-	-	hypothesis refuted
```

* `generator` ∈ {continue-census, carve-out-census, advice-audit, deferral-audit,
  carrier-rerun, control-operation, oracle-audit, hand}
* `verdict` ∈ {LIVE, FAIL-CLOSED, VACUOUS, INCOMPLETE, OUT-OF-SCOPE}
* `order` ∈ {1, 2} — **2 when the carrier is a campaign artefact** (repair, hardening, control,
  or remediation message). Leave blank unless `verdict=LIVE`.

**VACUOUS is a required verdict value and must not be folded into FAIL-CLOSED.** Six vacuity
traps have been caught this campaign; a probe whose positive control refused measured nothing
and must not count in the denominator as a clean negative. Yield is computed over
`LIVE + FAIL-CLOSED` only; VACUOUS rows are tracked separately as instrument failures.

**Driver rule.** Add to the window addendum: *"Every probe appends one row to `probes.tsv`
before you interpret it, LIVE or not. A probe you did not log did not happen."* Logging
*before* interpreting is deliberate — it prevents the denominator being written only when the
result is interesting.

**Back-fill.** ~60 probes from the 48 "no finding" handoff lines and
`carve-out-census-gen9.md`. Mark back-filled rows `note=backfill` — they are lower-confidence
than live rows and should be separable later.

**Acceptance.** `awk` over the TSV reproduces the three yield figures already stated in prose
("3 hits in 7 probes", "2 of 6", "top four gave three") to within the ambiguity of the prose.
If it cannot, the schema is wrong — fix it before back-filling further.

**Reported as.** From gen #17: the START HERE block leads with *yield per generator per
generation*, not "N routes found".

### Phase 2 — corrected verified fraction

**2.1** Extend `bin/count-trusted-directives.py` with `--metrics`, printing the pair
`(verified defs, live defs)` plus the marker histogram from Phase 3. Keep 459/484 as a column —
demote it, do not delete it; every historical figure is stated in it.

**2.2 — the correction.** Compute verified defs from **proof verdicts, not marker absence**:

* a mirror file counts only if it has a whole-file proof on record with `rc=0` and zero
  non-Valid goals (`getting-better/proofs49/*.rc` + the matching `.log`);
* within such a file, verified defs = defs − markers;
* files with no proof on record, or a stale one, contribute **0 verified defs** and are
  reported separately as `unproven-perimeter`.

Print three numbers, never one: `verified / live`, `unproven-perimeter defs`, and
`(MAX_UNMIRRORED_DEFS, MAX_UNMIRRORED_FILES)` from `check-mirror-coverage.py` (549/41).

**Acceptance.** The corrected fraction is published with the date of the *oldest* proof it
relies on. A proof older than the last emitter change to that file is stale and its file moves
to `unproven-perimeter` — *never inherit a gate verdict whose tree you cannot establish*
applies to this metric exactly as it applies to a battery.

**Falsification guard.** The fraction must not be allowed to rise because live defs were
deleted or moved to an unmirrored file. Assert `MAX_UNMIRRORED_*` did not rise in the same
commit; if it did, the rise is an artefact and must be reported as such.

### Phase 3 — marker reason taxonomy

**Pilot first — this is a hard gate.** Pick the mirror file with the fewest markers. Add
`reason:` to its markers only. Then:

1. `why3 prove --type-only` on the edited mirror;
2. emit and diff that file's `.mlw` against HEAD — **must be byte-identical**;
3. `check-self-annotate-sync.sh` + `self-annotate-mirror-check.sh` — delta must be zero.

**If the emission moves by one byte, stop and report it as a finding** — a comment-level token
changing emission is itself route-shaped, and it is the #96 pattern (a construct believed inert
that was not). Do not proceed to the other files.

Only on a clean pilot, tag the rest. Buckets:

```
reason: correctness:<name>     never convertible — cites the backlog paragraph
reason: cost-scale:<capability> convertible once <capability> is built
reason: spent-rc0              deliberately spent to buy rc=0 (e.g. core_ir_semantic untyped walk)
reason: unclassified           default; this bucket must go to zero
```

**Acceptance.** `unclassified` → 0. Every `cost-scale:*` value names a capability that exists
as a backlog item. The `spent-rc0` bucket makes the 451 → 459 rise legible for the first time —
today all 459 lines are byte-identical, so a considered assumption and a never-attempted stub
are indistinguishable.

**Standing caveat to record with the taxonomy.** A `correctness:` tag is a *claim*, and this
repo's boundary claims have been refuted repeatedly ("V1-floor REFUTED", "ten refuted
boundaries"). Re-probe a random 10 % per quarter via `probe-conversion-candidates.py`.

#### 2026-09-14 AMENDMENT — the in-band token is dead; the taxonomy lives in a side file

**The pilot gate above FIRED, and it did its job.** The in-band `reason:` token was REFUTED on
2026-09-13: `\trusted` is a parsed directive with a CLOSED grammar (`_parse_trusted` accepts only
`\trusted [reviewer: ID]`), so ANY trailing token makes Module 2 REFUSE THE WHOLE FILE — no
`.mlw` at all, which a common-files byte diff reads as zero changes (a false green). See
[`open-routes/finding-reason-token-refuses-the-whole-file.md`](open-routes/finding-reason-token-refuses-the-whole-file.md).
The original text above is kept as the record of the design that was piloted. **Do not add any
token to any `#@ \trusted` line, and do not repurpose `reviewer:`.**

**The design that replaces it (the finding's "option 2") — out of band, no language change, no
re-proof:**

* **Side file** `getting-better/trusted-reasons.tsv` — `#` comment header, then
  `file<TAB>qualname<TAB>reason<TAB>cite`, one row per live marker. `file` is relative to
  `src/self-annotate/src`; `qualname` is the FULL nested qualname (`Class.method.inner`), never a
  line number; a qualname collision within a file is disambiguated `#2`, `#3` in source order,
  numbered over ALL defs sharing the name (so converting one stub never renumbers a trusted
  sibling). Buckets are unchanged: `correctness:<name>`, `cost-scale:<capability>`, `spent-rc0`,
  `unclassified` (the default).
* **One attachment walk, not two.** The marker constants and `_block_marker_line` moved verbatim
  into `bin/trusted_markers.py`; `bin/count-trusted-directives.py` now imports them (its default
  and `--emit-dir` output and rc were diffed byte-identical before/after), and the checker keys
  its rows off the same enumeration.
* **Checker** `bin/check-trusted-reasons.py` (rc 0 OK / 1 defect / 2 refusal): both attachment
  directions (MISSING row -> prints the row to add; ORPHAN row -> prints the row to delete;
  duplicate key; unattached / multiply-attached marker), the reason grammar, the cite rule
  (`correctness:*` / `cost-scale:*` must cite a `driver-backlog.md` heading — exact heading text,
  or a substring of exactly one heading, outside ``` fences), the #44 zero-input guard (mirror
  files < `MIN_MIRROR_FILES`, missing/empty TSV, zero markers -> "THIS IS A REFUSAL, NOT A
  PASS"), the monotone-down `MAX_UNCLASSIFIED` ratchet, `--sync` (prints rows to add/delete;
  `--sync --write` applies them), `--seed`, and a histogram on every run.
  `--self-test` plants every defect in a temp copy and checks the rc and message.
* **Histogram in `--metrics`.** `bin/count-trusted-directives.py --metrics` now prints the
  reason histogram after the verified fraction (to stderr under `--json`).
* **Seeded mechanically, not speculatively.** 459 rows = 459 markers at `3c4f290c`. 458
  `unclassified`; ONE tagged, because a backlog heading names that exact function and its
  boundary tag: `frontend/Module5_IREmitter.py PyCSLToJSONEmitter._py_stmts_to_ir` ->
  `cost-scale:stmt-handler-dispatch`, cite ``L2 `_py_stmts_to_ir` `` (the 2026-08-27 measured
  erasure probe; its `SLabel`/`SProofAssert` constructors are still absent from `src/pycsl`).
  `MAX_UNCLASSIFIED = 458`.

**New acceptance for Phase 3 — DONE when:** side file + checker (both directions, grammar, cite,
zero-input guard, ratchet, sync mode, histogram) + negative tests + `--metrics` histogram have
landed. **That is now met.** The original acceptance "`unclassified` -> 0" is NOT dropped; it is
split out as its own track (below), because it is a multi-generation tagging effort, not a build.

**Follow-up, named and NOT done in this change: wire `check-trusted-reasons.py` into
`bin/run-soundness-planes.sh`.** Deliberately deferred — it moves the battery from 34 to 35
planes, a figure many status notes cite, so it should land as its own commit with those notes
updated in the same pass. Until then the plane is run by hand and via `--metrics`, and drift
between the markers and the side file is caught only when someone runs it.

**Tagging track (separate, multi-generation, its own ratchet).** Drive `unclassified` 458 -> 0
by lowering `MAX_UNCLASSIFIED` monotonically, never raising it. Rules: a `correctness:` or
`cost-scale:` tag must cite the backlog heading that MEASURED the boundary (write the heading
first if the paragraph lacks one); `spent-rc0` is for an assumption deliberately bought to reach
rc=0 and should be applied at spend time; when in doubt, leave `unclassified`. The standing
caveat above (re-probe 10 % of `correctness:` per quarter) applies to the side file unchanged.
A NEW marker lands as `unclassified` via `--sync --write` and breaks the ratchet — that friction
is intended: it forces classification when the assumption is spent, which is exactly what makes
a rise like 451 -> 459 legible.

### Phase 4 — silent-raise burn-down (the actual trust reduction)

**This is the only item here that reduces what is assumed without needing a capability.**

70 stubs whose live body raises directly and whose stub declares no `#@ raises`. A `\trusted`
val with no `raises` clause tells Why3 *the call cannot raise* — strictly stronger than "a
reviewer trusts this body".

**Method.** Batch by mirror file. Per batch:
1. add `#@ raises <E> when <condition>` using the in-tree idiom (`ir_schema.py:171`);
2. `why3 prove --type-only`;
3. whole-file re-proof of that mirror — **one at a time, never alongside the suite**;
4. lower `MAX_SILENT` in `check-trusted-raises-honesty.py` by the batch size;
5. commit with the checkpoint line.

**Never raise `MAX_SILENT` to make the ratchet pass.** Gen #16 hit 71 > 70 and repaired it the
right way — by declaring, not by moving the bound. That precedent is the rule.

**Honesty constraint.** `raises E when True` on a stub whose live body raises only on a path
the `requires` excludes is a *false* declaration that happens to satisfy the plane. Use the
real condition where expressible; where it is not, declare the over-approximation **and record
in the commit that it is one**. The plane's own header admits it over-counts these.

**Cheapness note worth exploiting.** Gen #16 measured that a `raises` on a val declared but
never called in-file adds no VC. Order the batches by that property — the no-call files are
nearly free.

**Acceptance.** `SILENT` 70 → 0 with `MAX_SILENT` lowered monotonically, every touched mirror
re-proved rc=0, fidelity delta zero throughout.

### Phase 5 — blind recapture window

**Setup.** A fresh agent window at HEAD with **the route ledger, handoff, and progress log
withheld**. Fixed budget: 40 probes. Same CPython-ground-truth rule, same both-directions
requirement. The repo already has this discipline (the skill's independent fable reviewer;
the backlog's "FRESH-EYES DELEGATION BROKE THE FALSE FLOOR").

**Read out.** `n₂` = its LIVE findings; `m` = how many are already-known routes (closed or
open). Report `m/n₂`.

**Interpretation — bounded, per §0 challenge (2):**
* `m/n₂` low → **strong evidence against convergence**, plus a list of the generators the
  driver lacks. This is the informative direction.
* `m/n₂` high → weak evidence *for* convergence. Shared method inflates `m`, so `N̂` is a
  **lower bound on what remains**. Never report it as "nearly done".
* `n₂ = 0` → **no measurement**, not convergence. Same rule as a probe whose positive control
  refused. Record it as an uninformative sample and say why.

**Scheduling.** Needs prover time; run at a quiet point on the box, never during a suite.

### Phase 6 — generated differential sampler

The standing hunter-independent instrument, replacing the blind agent for routine measurement.

**Build.** `bin/gen-differential-drivers.py` emitting ~200 small total programs per run from
templates over constructs the campaign has touched — field literals, `__init__` capture shapes,
aliasing, `is`, dict/set ops, `del`, `assert`, frames on trusted stubs, renamed parameters —
into `test-suite/value-differential/generated/`, which the standing run skips (follow the
`negative-test/` precedent). CPython is the oracle; the existing plane runs over it.

**Yield** = RED / generated, reported per template family.

**A RED here outranks a RED from the driver**, because the sampler did not know what it was
looking for. That is the whole point of building it.

**Converging** = RED per 200 falls to 0 across three consecutive runs **with the template set
frozen**. Adding a family resets that clock for the new family only.

**Blind spot to state alongside every run.** Constructs outside the template set; anything
needing `requires` richer than `\result == <int>`; and unsound *refusal message text* — #90's
remediation-advice exploit is invisible to any program-level sampler, because the defect was in
English prose telling the user what to write.

---

## 3. Cadence and reporting

| when | what | where |
|---|---|---|
| every probe | one TSV row, before interpreting | `probes.tsv` |
| every generation | yield per generator; second-order share; corrected verified fraction; `SILENT` count | START HERE block |
| every 2–3 generations | blind recapture `m/n₂` with its bound caveat | handoff + this file's log |
| per capability landing | `probe-conversion-candidates.py` CLEAN count | backlog |
| per quarter | re-probe 10 % of `correctness:` markers | backlog |

**The generation report leads with yield, not with a route count.** A count that only goes up
cannot say "nearly done", and the campaign has been steering by one for six generations.

---

## 4. What this plan does not fix

* **The hunter-independence gap is only partly closed.** Phase 6 adds one independent
  instrument over a *template set someone chose*. Templates are a generator, so template
  coverage is the same blind spot one level up. It is a real improvement over zero independent
  instruments, not a solution.
* **Nothing here measures whether a verified body's contract is meaningful.** A def can be
  proved against a vacuous `ensures`. The vacuity planes cover part of this; the verified
  fraction does not, and should never be quoted as if it did.
* ~~**The refusal-text surface stays unmeasured.**~~ **MEASURED IN FULL (#49, gen #30.)**
  The census is 108 advice-bearing messages, not 62 — the earlier count missed every raise
  whose exception class is imported under a LOCAL ALIAS, which is every route refusal this
  campaign has landed in `pycsl.py` since route #29. **All 108 have now had their advice
  FOLLOWED AND RUN**: a file written the way each message says, compiled, verdict recorded,
  in `bin/check-refusal-advice-audited.py`. **102 work.** The six that did not were all
  repaired the same evening and fail in four distinct ways — UNSPELLABLE (a `#@` directive
  named without its argument: `#@ shared`, `#@ touches_field`), UNTRIED (an explicitly-called
  DUNDER does not carry its contract; `Optional[List[T]]` did not compile — **twice the
  compiler told a user to write a program it cannot compile**), and AMBIGUOUS (one repair
  needing an unstated LOCAL instance; one OR-list whose first disjunct is really a
  conjunction). **Route #215 came out of auditing one of them.** The audit is still MANUAL
  — the plane cannot check prose — but it is now DONE, RECORDED and RATCHETED, keyed on a
  message signature plus a whole-message HASH so an edited message re-opens its verdict.
  The remaining prose risk is the one this method cannot reach: a message that is
  followable AND misleading.
* **The second-order rate may be structurally irreducible.** 6 of the last 22 routes were
  repairs-of-repairs. Driving that to zero assumes repairs can be written that never introduce
  a narrower version of the bug they fix — which the record does not yet support. Track it;
  do not promise it.

---

## 5. First three actions, concretely

1. Create `probes.tsv` with the schema in Phase 1 and add the one-line driver rule to the
   window-#6 addendum. No prover time; can be done while gen #16 runs.
2. Recompute the verified fraction from `.rc` evidence (Phase 2.2) **before** 28.2 % is quoted
   anywhere. Publish the corrected triple with the oldest-proof date.
3. Run the Phase-3 pilot on one mirror file. If emission moves, that is a finding and the
   taxonomy stops; if it is byte-identical, tag the rest and start the Phase-4 burn-down with
   the no-call files first.
