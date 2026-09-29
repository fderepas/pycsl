# START HERE — gen #33 FINAL STATE (2026-09-29, window #8)

Deadline **1790873022** = Thu Oct 1 16:43:42 UTC 2026 (written by the supervisor, never recomputed).
Do NOT push. Everything below is committed and the tree is clean.

## THE METRIC — quote BOTH numbers

    markers 449 · grep-substring 477 · offset 28 · attached 449 · unattached 0

**Unchanged for the whole generation, and that is the correct shape**, not a stall: gen #33 paid the
soundness ladder. A route found and closed, three new planes, two ratchets tightened and a refuted
hypothesis all cost the trust surface exactly nothing. Do not chase the metric.

## THE STATE GEN #34 INHERITS

Fully gated at battery #6 plus a plane-set re-run, **nothing owed**:

    planes   82/82 `--slow`, rc=0        (MIN_PLANES 54)
    corpus   1379 baseline / 1379 candidate, 1 MOVED + 2 GONE, both DECLARED BY NAME, 0 APPEARED
    pyref    2199/2199, 0 MOVED          (TWO comparisons, one per emitted tree — lesson (c4))
    suite    4038/4056, 18 CONFIRMED FAIL = the standing baseline, `grep -c XPASS` = 0 over the FULL log
    corpus files 1917 · 57 commits this generation

Ratchets, none loosened: `MAX_UNCLASSIFIED` 279 · shadowed-selfcalls 14/119 · assigns-writes TRAP
2989 / **HOLE 0** · assigns-underdeclaration TRAP 18 / HOLE 0 and TRAP-T 148 / **HOLE-T 0** ·
refusal-witness floor **208** / ceiling 5 · advice floor 128 · raises-honesty silent **61**.

## THE ORACLE THAT LANDED — READ THE SCOPE LINE, IT IS THE POINT

`bin/run-self-annotation-suite.sh` finished its FIRST COMPLETE GREEN RUN of the campaign. Verified
from the **rc file**, with the tally COMPUTED not quoted (lesson (m4)): `sas2.log.rc` = **0** (run 1's
= **124**), **38 `[PASS]` / 0 `[FAIL]`**, its own line `Self-annotation: 38/38 proved`.

  * **COST 14h31m22s** (`09:44:10Z` → `00:15:32Z`). **Quote ~15 h at this concurrency.** The 18-24 h
    and 6-12 h figures in circulation were extrapolations from a TRUNCATED run; this is the clock.
    Corrected in place further down this file.
  * **THE MEMBER COUNT IS 38, NOT 40.** "25 of 40" was run 1's truncated view, repeated in prose since.
  * `pure_ast.py` PASSED — the member run 1 never reached. `errors.py` passed in BOTH copies.
  * **SCOPE: it ran at commit `11ee64a7`, a GEN #32 commit**, in the frozen worktree
    `/home/fabrice/git/pycsl-g32wt2`. **EVERY gen #33 increment is OUTSIDE this verdict.** A green
    does not stand in for a tree it never saw. Re-running is a ~15 h item; do NOT put it in a battery.

## WHAT GEN #33 RESOLVED

| item | verdict |
|---|---|
| **route #228** — a false postcondition PROVED via a `stable_hash` collision | **BROKEN**, repaired, gated |
| **route #229** — a `global` inside an exec'd text defeats the "discarded snapshot" | **BROKEN**, repaired, gated |
| the frame plane's population hole — 498 methods outside `check-trusted-frame-honesty` | **FAIL-CLOSED**, TRAP 18 / HOLE 0, new plane |
| the same, TRANSITIVELY | **FAIL-CLOSED** at 8x, TRAP-T 148 / HOLE-T 0, gated |
| **ladder item 1 (#64)** — a mechanical cause of the int-erasure seam | **REPRODUCED from three lines, then its payoff REFUTED** |
| `check-trusted-raises-honesty` ratchet one loose for generations | tightened 62 → 61, **not my improvement, only my noticing** |

### Route #228, and the part worth carrying is NOT the collision

`struct.pack('<bb6x',1,2)` (8 bytes) and `struct.pack('<xxxxxxxxhxLxxxxxxxx',1,2)` (23 bytes) both
emit `(struct_pack_i2 1322019588 1 2)` — ONE TERM — so `len(a) == len(b)` proved `Valid, 156 steps`
and `\result == 1` was PROVEN while CPython returns 0. The non-colliding control did NOT prove.

**The collision was GEN #30's finding.** `bin/check-hashed-literal-purity.py` already had the same
pair, the pure-`val function` discriminator, and the 22 baselined struct rows — and ended that
baseline *"searching for one is recorded as the follow-up rather than done here."* **It sat inside a
GREEN GATE for three generations.** Doing it takes seconds.

>>> **LESSON (a5): A BASELINE THAT RECORDS ITS OWN FOLLOW-UP IS AN OPEN ROUTE WITH A GREEN GATE IN
>>> FRONT OF IT.** An allowlist row is read once, when written; after that the gate prints OK. Grep
>>> every gate's baseline prose for `follow-up`, `not done here`, `rather than done`, `the shape to
>>> look for`, `TODO`. I ran that sweep: 4 candidates, 1 live — and it produced the frame finding.

Repair: **not a wider hash** (that is #227's lesson in a new costume). The premise is decidable, so it
is CHECKED — and after `check-mirror-type-only` refuted my placement, it lives at the one destination
that can conclude a falsehood. See lesson (c5) below.

### Ladder item 1 (#64): the seam HAS a cause, and the cause does NOT explain the markers

    si = set(); si.add(1)      # int kappa    -> MONO arm
    ss = set(); ss.add("a")    # string kappa -> POLY arm

emitted `map int (option int)` and failed L3-tc *"type string, but is expected to have type int"* —
gen #32's own `string vs int` row. **Each set ALONE type-checked**, so it is an INTERACTION no
per-feature probe could find. Cause: the decl is chosen PER SITE while `_add_abstract_op` arbitrated
the same-arity clash by **"keep longer"**, and the int-monomorphic spelling is longer in all three
affected symbols (`snapshot` by TWO characters), winning in BOTH registration orders. `statements.py`
says *"one decl serves every map write in the module"*; which one was never decided.

**AND THE PAYOFF IS ZERO, MEASURED.** One instrument, two passes, the 37 markers whose recorded
blocker is a string↔int mismatch: **BEFORE 37 L3TC-FAIL / AFTER 37 L3TC-FAIL, `diff` of both
manifests SORTED — IDENTICAL, 0 MOVED, 0 LOWER.** Predicted "0 to 2, most likely 0" beforehand. So
the tiebreak is a real mechanism and explains NONE of the 37: **the hypothesis is REFUTED, which
narrows #64 by removing a candidate.** Gen #31's three seam repairs moved 11 of 115; this moves 0 of
37. Artefacts: `seam-{before,after}-gen33.txt`, `seam-string-int-targets-gen33.tsv`, and the runner.

What it DOES fix is real and is corpus **1916**, which now proves.

### Route #229, and it came from the campaign's OWN #1 generator

    N = 3
    def rebind() -> int:
        code = "global N\nN = 5"
        exec(code)
        return 0
    #@ ensures \result == 3
    def read() -> int:
        return N          # PROVED. CPython returns 5 after rebind().

*Read the "how to fix this" line of a refusal as an attack surface.* The silent-name refusal's advice
ended **"keep a dynamic `exec`/`eval` out of module and class-body scope"** — naming a SCOPE BOUNDARY
as safe — and the detector's comment justified it: *"assignments made by a bare `exec`/`eval` go to
the LOCALS mapping, which … is a discarded snapshot inside a function."* True of a plain assignment.

>>> **A SCOPE ARGUMENT ENUMERATES THE BINDING FORMS ITS AUTHOR PICTURED, AND `global` IS THE BINDING
>>> FORM WHOSE WHOLE PURPOSE IS TO DEFEAT THE SCOPE IT RESTS ON.**

That detector is one of the best-audited comments in the tree — six measured falsehoods, two
abandoned spelling rules (the `:=` cut and the token cut, each recorded with the witness that walked
past it), a census over five trees. **What survived was the one premise nobody re-read.** Three
neighbouring shapes were already refused (module-scope exec, constant exec in a function, dynamic
`eval` reaching `globals()`), which pinned the population to one shape and supplied the non-vacuity
evidence.

Fix: a NON-CONSTANT `exec` now reaches wherever it stands, as a non-constant `eval` already did. **Not
a spelling rule** — the text is dynamic, so the emitter cannot read it and any rule about its contents
is unfounded by construction.

**OPEN FOLLOW-UP THIS CREATED, and it is a real question, not a tidy-up:** corpus 0638/0639 now fail
by REFUSAL rather than by the mechanism they exist to exercise, so **the `\in_scope` havoc and
frame-taint machinery are no longer reachable from the corpus language. IS THAT MACHINERY NOW DEAD
CODE?** Each file says so in its own docstring. Nobody has answered it.

**AND A PROCESS NOTE WORTH MORE THAN THE ROUTE:** I declared 3 GONE in the byte-diff and the
comparator answered *"--expect-gone 0644 was declared but it still emits."* 0644 had ALREADY been
refused before the repair (measured: no `0644.mlw` in the baseline emit dir). **A declaration is a
PREDICTION, and an over-declaration is as wrong as an under-declaration** — `--expect-gone` /
`--expect-moved` are a two-way contract, and they caught an overstatement of my own change's effect
before it became the next generation's false premise.

## THE LESSONS THAT BIND GEN #34 (all carved into the skill, both copies synced)

  * **(a5)** a baseline that records its own follow-up is an open route with a green gate in front of
    it — and *search the PROPERTY the gate names, not the EXAMPLE its comment pictures* (gen #30's
    recorded shape was too narrow; searching only it would have "confirmed" the baseline).
  * **(b5)** **a probability in a justification is a check nobody wrote.** Grep the TCB for `w.h.p.`,
    `unlikely`, `in practice`, `should not happen`. **Never answer one with more bits.** And check the
    MODULUS: a `% 100000` after a hash is four orders of magnitude more collidable than the hash.
  * **(c5)** **"LIVE-SIDE ONLY" IS NOT "MIRROR-INERT".** The mirror is emitted with
    `--import-path src/pycsl`, so a mirror's call resolves to the **LIVE** definition and never reads
    the mirror's `\trusted` copy. A `raise` in a shared leaf is inherited by every mirror that CALLS
    it, through the EXCEPTION SET, not through fidelity. `grep -rln '<helper>' src/self-annotate/src/`
    before calling any live-only edit free. **Verify BOTH ends** — a plane RED now is only yours if it
    was GREEN then, and a worktree at the pre-change commit makes that a measurement.
  * **(d5)** **PREDICT THE LEDGERS, NOT ONLY THE EMISSION.** Six plane REDs this generation, ALL
    mine, NONE predicted, one predicted GREEN — while every emission prediction was exact across four
    consecutive batteries. Each was a ledger indexing what I touched: corpus file → vacuity CEILINGS +
    purity BASELINE + suite totals; refusal added/**edited**/**moved** → witness census (keyed on
    MESSAGE TEXT) + advice audit; `raise` in a method with a `\trusted` mirror stub → the raises
    ledger, **once per mirror file that stubs it**. **Re-measure a stale ledger row, never hand-edit
    it.** When a ratchet objects, **ask first whether the ratchet is RIGHT** — twice it was, and the
    fix was to change the design. And **check whether an improvement is YOURS before banking it.**

## LADDER FOR GEN #34, in order

0. **READ THE MARKER'S OWN COMMENT BEFORE CONVERTING IT** (gen #32's rule, still first). Backlog #73's
   harvester turns prose already paid for into gate-enforceable classification at no prover cost —
   re-run it whenever the ratchet stalls.
1. **#64 remains item 1, with one rung now CLOSED.** The arbitration is NOT the cause of any recorded
   marker — do not re-derive that, the manifests are committed. The screen's `int` vs real-type rows
   still need a cause, and the instrument to test any candidate now exists and is cheap (~7 min a
   pass over the 37 targets). **Use it before building anything.**
2. **Is the `\in_scope` havoc / frame-taint machinery DEAD CODE now?** Route #229 made dynamic `exec`
   unreachable from the corpus language, and 0638/0639 were its only demonstrations. This is the
   newest open question and it is cheap to start: find every emitter path gated on a dynamic exec.
3. **Two of the three defect rows gen #32 filed away from the seam are still unprobed** — the emitter
   emitting syntactically INVALID WhyML for a ported body (2 markers, `_parse_contract` /
   `_parse_atom_name`; gen #32 rightly called it "not a modelling gap; it is a bug"), and a
   name-rebinding REFUSAL whose population nobody has counted (4). **The third became route #229.**
4. **The 18 under-declared `#@ assigns` clauses** (TRAP 18, all `\trusted`, listed by name in the
   plane's `TRAP_BASELINE`). Each is a one-line fix that changes the stub's emitted `writes` in every
   importing mirror, so it owes the re-proof bill lesson (k4) prices. TRAP should come DOWN.
5. Gen #32's queue, untouched by gen #33: **#69 item 2** (a RETURN annotation carrying the `hval`
   codomain), **#65** (route #227's container carrier), **#68** (an imported contract's free module
   constant), **#67's five MISSING declarations**, and the **5 unaudited refusal-advice sites**.
6. **`pure_ast.py` (178 markers) is still unscreened** by the conversion screen, plus a few small
   files. Gen #32 expected the same distribution; it is worth finishing and costs no prover time.

## PROBED THIS WINDOW WITH NO FINDING — DO NOT RE-PROBE

  * `stable_hash`'s NON-pure destinations (bare `val`, dict keys, list literals, set literals,
    `getattr_<cls>_poly`) — all VACUOUS or faithful; the table is in the route file.
  * `setattr_<T>_poly` declared "EFFECT-FREE" over a mutated field — FAIL-CLOSED: its only gated
    method is NET-NEUTRAL (saves, sets, restores in a `finally`).
  * the `% 100000` name folds — no live clash; the only same-name clashes are the poly/mono trio and
    two binder-grouping pairs, and a gate now censuses all 272 declaration names.
  * `check-collapsed-option-reads`'s `UNPROBED` verdict class — reports 0, the class is unused.
  * **Three "findings" this session were my own regex artefacts** (`val constant <name>` capturing the
    keyword, prose matching `function <word>`, `%s` read as a name). **Read the outlier rows.**

---

# START HERE — gen #32 FINAL STATE (2026-09-28, window #8)

Deadline **1790873022** = Thu Oct 1 16:43:42 UTC 2026 (written by the supervisor, never recomputed).
Do NOT push. Everything below is committed.

## THE METRIC — quote BOTH numbers

    markers 449 · grep-substring 477 · offset 28 · attached 449 · unattached 0

It sat at **450** for most of the generation, and that was the CORRECT shape while the window paid
the soundness ladder — a refusal, a re-port, three new planes and a widened detector all cost the
trust surface nothing. It came DOWN to 449 at the end by an honest conversion (`as_dict`, below). Do
not chase the metric and never re-baseline anything to move it. The offset is now **28** (not the
historical 25, nor the 27 this window started at): the new comment explaining the conversion quotes
the marker, and `bin/count-trusted-directives.py` prints the gap on every run.

## WHAT GEN #32 RESOLVED

| item | verdict |
|---|---|
| the in-flight `run-soundness-planes.sh` patch (window #8's mandated FIRST ITEM) | **COMMITTED** `a1676339`, re-measured not inherited: 55/55 fast, both newly-registered planes green |
| **route #227** (NEW, Sev-1) | **FOUND and CLOSED, FULLY GATED** `535a1bb7` |
| **backlog #63** (the top of the ladder, a SOUNDNESS item) | **CLOSED and GATED** `a56dcd85` |
| **backlog #66** (the advice detector's verb list) | **LANDED** `5eaec302`, all twelve new sites audited |
| **backlog #67** | **PLANE BUILT** `44227973`, ratchet set, negative-tested |
| `check-stdlib-modules-verify` standing RED (gen #31's handoff) | **RETIRED** — 104 modules, **84** VERIFY (was 83), neither failure mode firing |
| **backlog #69 item 1** — the suite's ONLY failure | **FIXED**, and the same repair CONVERTED a marker: **450 -> 449** `0dcce16b` |
| `bin/run-self-annotation-suite.sh` — the unscheduled oracle | **RUNNING**, see below |

**Gate verdicts, all with predictions written BEFORE the run and all exact:**

* gate 227 — corpus byte-diff 1378/1379 **0 MOVED, 1 declared GONE**; pyref **2199/2199 0 MOVED**;
  planes **77/77 `--slow`**; suite **4034/4052**.
* gate 63 — corpus **1379/1379 0 MOVED**; pyref **2199/2199 0 MOVED**; mirror **53/53, 2 MOVED both
  accounted for line by line**; `statements.py` whole-file **18896 Valid, 0 non-Valid**; planes
  **78/78 `--slow`**; suite **4034/4052 — 3136 PASS / 898 XFAIL / 18 FAIL, ZERO XPASS MEASURED**.
* gate ERR (the `as_dict` conversion) — corpus **1379/1379 0 MOVED**; pyref **2199/2199 0 MOVED**;
  suite **4034/4052, `grep -c XPASS` = 0**; the 15 owed hval-propagation re-proofs **15 of 15, rc=0,
  zero non-Valid**; planes **78 of 79 — ONE RED, and it was MINE.**
  `check-shadowed-selfcalls` went 14 -> 15: *"a conversion landed whose body no caller can see"*.
  Converting `as_dict` gave `self.message()` its first live intra-class call site and the default
  lowering of such a call is a receiver-less abstract `val self_message_0` with an unconstrained
  result. **Fixed at the CAUSE** with `#@ sibling_concrete` on `message()` (the sanctioned opt-in for
  a cheap leaf) -> **14/119, the exact pre-conversion figures, ratchet never touched**, the abstract
  `val` gone from the emission, and the call now `(HStr (pycslerror__message self))` — so the
  conversion ended up STRICTLY STRONGER than when first banked. 4 mirrors moved and re-proved.
* gate SC (the `#@ sibling_concrete` fix) — **GREEN ON EVERY LEG**: mirror **53/53 0 MOVED**, corpus
  **1379/1379 0 MOVED**, pyref **2199/2199 0 MOVED**, planes **79 of 79 `--slow`** with
  `check-shadowed-selfcalls` **ok at 14/119**, suite **4034/4052, `grep -c XPASS` = 0**. Every
  prediction exact. **THE GENERATION IS FULLY GATED — nothing is owed.**

**Baselines for gen #33:** suite **4034/4052**, standing **EIGHTEEN**, a 19 is a REGRESSION, zero
XPASS. Planes **78** with `--slow` (50 fast array + 5 conversion + 23 slow). Corpus 1379 emitting
`.mlw` + 2199 python-reference.

## ROUTE #227 — THE ONE SOUNDNESS ROUTE, AND ITS GENERATOR IS THE THING TO CARRY FORWARD

    v = None
    return v - v + 3      PROVED \result == 3 under `#@ no_exception \all`;  CPython: TypeError

The carrier was the campaign's OWN repair. Routes #44/#184/#191 replaced a definite `0` with the
opaque `val function pycsl_none : int`, which closed every VALUE-dependent falsehood and left every
consequence INVARIANT under the value, because **the opaque kept the TYPE `int`**.

>>> **WHEN A REPAIR ANSWERS A WRONG VALUE WITH AN OPAQUE, IT HAS MOVED THE FALSEHOOD FROM THE VALUE
>>> TO THE TYPE.** Re-probe the repaired carrier with an expression whose result does NOT depend on
>>> the value — `x - x`, `x * 0`, `x < x`, `x // x` — and with the `no_exception` claim, which is a
>>> statement about the type alone. `v == 0` is the probe the repair was built to defeat; `v - v` is
>>> the one nobody wrote. Route #44's OWN witness 1060 is this shape with `x + 5` — value-DEPENDENT —
>>> and its docstring says "an equality-only fix would have been the same mistake one operator
>>> later." It was arithmetic-aware and still stopped one ALGEBRAIC IDENTITY short.

Repair: `_erased_truthy_locals` now also REFUSES (arithmetic + strict order on a definitely-`None`
operand), which is what route #50's facts were already used for. Witnesses 1909-1913.
**ONE ARM SURVIVES — backlog #65**, the `None` that reaches the operator through a CONTAINER read
(`d[k] = None; v = d[k]; v - v`), where the None-ness is a VALUE fact no syntactic record can carry.

## THE CONVERSION, because it is the template for the next ones

`errors.py::PyCSLError.as_dict` carried `#@ \trusted` with the comment *"builds a dict (PyCSL cannot
model dict construction here yet)"*. **The comment was what had gone out of date.** The certified
axiom-free `hval` model (`HStr | HInt | HArr hval_list | HMap hpairs | HNode`, co-landed with the
Rocq/Lean `Phase2f_PyVal` cert) models exactly this dict. Annotating it `Dict[str, PyVal]` retires the
marker AND fixes the self-annotation suite's only failure, because the LIVE twin was that failure.

Emitted body — native string keys, each value tagged by its TRUE kind, real record fields, a `let`
with a body, `assigns \nothing` discharged by four `old` equalities. Not a facade:

    let pycslerror__as_dict (self: pycslerror) : map string (option hval) =
      map_update_some (… (const (None: option hval)) "code" (HStr self.pycslerror_code))
        "stage" (HStr …) "filename" (HStr …) "line" (HInt self.pycslerror_line)
        "message" (HStr (self_message_0 ()))

**MEASURED CAPABILITY BOUNDARY (backlog #69 item 2, still open):** `Dict[str, PyVal]` selects the
`hval` codomain from a **declared LOCAL or PARAM and NOT from a RETURN annotation**. That is why the
literal is bound to `_d` before being returned, and the workaround is load-bearing until item 2 lands.

**AND THE BILL, which is lesson (k4):** I predicted 2 mirror emissions would move and **15** did —
every importer of `errors.py` gains the ~62-line `hval` THEORY in its preamble. All fifteen were
re-proved: **15 of 15, rc=0, zero non-Valid**, 6h09m, including `expressions.py` (2h21m) and
`statements.py` (2h19m). *A stub in a LEAF module is cheaper than an identical stub in a SEED module
by exactly the number of importers, and nothing in the triage currently says so.*

## LADDER FOR GEN #33, in order

0. **READ THE MARKER'S OWN COMMENT BEFORE CONVERTING IT.** The cheapest rule on this page, and gen
   #32 broke it twice in one afternoon. `Module2_Parser::_parse_assigns` is TWO lines, CLEAR on the
   #72 preflight, in a file that re-proves in seven minutes — and its comment reads *"Stays
   `\trusted` (builds an assigns target list — family-B list boundary)"*. Backlog **#73** harvested
   these: **22 of 449 markers carry a recorded stay-trusted / RE-TRUSTED / CERTIFIED-BOUNDARY verdict
   in their own adjacent comment**, eleven in `pure_ast.py` alone. The sweep is committed
   (`getting-better/open-routes/harvest-stub-comment-verdicts-gen32.py`); **re-run it whenever the
   ratchet stalls**, because it turns prose somebody already paid for into a gate-enforceable
   classification at no prover cost.

1. **BUILD THE INT-ERASURE SEAM (backlog #64), AND KNOW THAT NOTHING ELSE ON THE COUNT TRACK IS
   AVAILABLE UNTIL YOU DO.** Gen #32 screened **31 of the 53 mirror files — roughly 215 candidates —**
   with `bin/probe-conversion-candidates.py` (ports the live body un-trusted, emits, classifies,
   ALWAYS restores; ~10 s each, no proof time, foreground). Result:
   **L3TC-FAIL ~198 · ERASURE 7 · NO-LIVE-SOURCE 11 · CLEAN 1** — and the single CLEAN,
   `Module2_Parser::_err`, is one backlog #73 had already harvested as gen #31's RE-TRUSTED
   input-blind conversion. **ZERO actionable conversions across 31 files.**
   Roughly **55 of the 60 distinct blocker rows are one wall wearing many faces**: `int` against
   `array int` / `array string` / `string` / `emit_ir` / `seq int` / `option int`. Backlog #62 named
   that seam "the number-one wall, 103 of 116 markers" from one direction; this screen is the
   independent confirmation from the other — I did not go looking for it, I screened everything, and
   the seam is what came back, in files #62 never measured. **#64 is right that the unit of work is
   one marker's whole CHAIN.**
   Two rows deserve a separate look, being a different class of defect from a type mismatch: the
   emitter produced **syntactically INVALID WhyML** for a ported body (`_parse_contract`,
   `_parse_atom_name`), and two more report "a name's runtime value is not the one the model reads".

2. **Backlog #72 — NOT A WORK QUEUE. Its value is the EXCLUSION, and gen #32 proved that the hard
   way.**
   Gen #32 refuted two size-picked conversion candidates in twenty minutes (lesson (o4): *a
   relocation's cost is its CALLEE CLOSURE, not its line count*) and then built the instrument that
   generalises it: `getting-better/open-routes/preflight-marker-callee-closure-gen32.py` walks every
   marker's live body against the constructs this campaign has MEASURED as blocked. All 449 markers,
   in seconds: **210 BLOCKED / 239 CLEAR**, and joined against `trusted-reasons.tsv` the shortlist is
   **151 CLEAR-and-unclassified**. Read 151 as an UPPER BOUND — the filter is CALL-shaped while the
   biggest wall (int-erasure, 102 markers) is TYPE-shaped and only the TSV join catches it, and
   "unclassified" hides already-refuted candidates (the two smallest survivors are exactly the ones
   gen #32 and #31 measured as unlandable). Do the cross-reference FIRST — it tightens
   `MAX_UNCLASSIFIED` for free — then screen the residue port -> `--fun` -> classify -> REVERT **in
   the FOREGROUND**, then convert **per destination FILE** so one re-proof covers a batch.
   **THE SCREEN SAYS THE SHORTLIST'S HIT RATE IS ZERO.** My call-shaped preflight said 17 CLEAR for
   `Module2_Parser.py`; the screen says 0 convertible. The CLEAR bucket is exactly where the TYPE
   seam lives, invisible to a call-shaped filter as documented — so **use the preflight only to
   EXCLUDE cheaply (210 BLOCKED by a known method wall, 49 NET-ZERO) and use the SCREEN to rank.**
   **THE INSTRUMENT CONVERGED FOUR TIMES AND THE SHORTLIST IS 103, NOT 151** — each tightening removed
   candidates that would have wasted a build: 151 -> 153 (re-derived) -> 143 (a missing FREE callee
   that is not int-shaped is NET-ZERO, lesson (r4)) -> **103** (a `self.<m>()` the DESTINATION FILE
   lacks auto-synthesizes a RECEIVER-LESS `val`; that one check moved FORTY markers out of CLEAR).
   Standing: **449 = BLOCKED 210 / NET-ZERO 49 / CLEAR 190**, of which 103 unclassified.
   **STILL BLIND — do not over-read a CLEAR:** `%` string formatting, KEYWORD arguments, host-`ast`
   node types, and above all the int-erasure SEAM, which is type-shaped and invisible to a call-shaped
   filter; always join against `trusted-reasons.tsv`, which classifies it for 102 markers already.
   BATCH BY FILE on this generation's measured re-proof costs: `Module2_Parser.py` 19 markers / 6m59s,
   `Module3_Weaver.py` 11 / 3m11s, `Module1_Ingestor.py` 8 / 13s, `pure_ast.py` 30 / **2.5h**,
   `expressions.py` 14 / 2h21m, `statements.py` 9 / 2h19m.
3. **Backlog #69 item 2 — make a RETURN annotation carry the `hval` codomain**, so the
   declared-local workaround above stops being load-bearing. The arm is byte-inert today (before this
   generation, no `.py` file in the tree used `Dict[str, PyVal]` at all), so there is little to
   regress. And re-scan for OTHER `\trusted` markers whose stated reason is "cannot model dict
   construction" or similar — `as_dict`'s comment was stale, and a comment that names a capability
   the campaign has since built is a conversion waiting to be noticed. **That is the cheapest lead
   on this list: grep the 449 markers' reasons for capabilities that now exist.**
4. **Backlog #65** — route #227's container carrier. Two named reopening capabilities, cheapest
   first: refuse on a local read from a container whose DECLARED codomain is `Optional[...]`
   (needs its own census), or route #56's general repair (a distinguishable `None` in the value model).
5. **Backlog #68** — an imported contract's free module constant lowers to an opaque `val constant`,
   so route #143's advice is followable-but-unprovable. Fold against the DEFINING module's binding,
   gated on the name being a module CONSTANT (folding a mutable global would be unsound).
6. **Close #67's five MISSING declarations** — each is a latent int-erasure of #63's exact shape.
   COST/SCALE: each declaration changes the emitted WhyML and owes a whole-file re-proof of
   `Module6_WhyMLTranspiler.py`, `functions.py`, `statements.py`.
7. **Backlog #64 (now item 1 above; the original note follows)** — the int-erasure seam, one marker's WHOLE CHAIN at a time. Still the #1 wall.
8. The five refusal sites still unaudited in `check-refusal-advice-audited` (4 in `pycsl.py`, 1 in
   `Module5_IREmitter.py:5205`) — pre-existing debt, and now the only debt in that plane.

## NEW PLANES AND RATCHETS THIS GENERATION — do not loosen any of them

    bin/check-assigns-writes-survival.py        TRAP 2989 / HOLE 0   (SLOW set, shared emission)
    bin/check-sibling-concrete-field-decls.py   MISSING 5 / MISMATCH 2 all justified BY NAME
    check-refusal-witness-coverage              demonstrated floor 206 -> 207
    check-refusal-advice-audited                audited floor 116 -> 128, advice-bearing 121 -> 133
    check-sibling-concrete-fidelity             DIVERGING_BASELINE tightened to the EMPTY SET
    check-trusted-reasons                       MAX_UNCLASSIFIED 286 -> 285 -> 284 -> **279**,
                                                and the TSV's FIRST `correctness:` row ever
                                                (`pure_ast.py::_set_ctx`: converting it would
                                                 make the model assert the false "ctx is
                                                 still Load", so the trusted `val` is the
                                                 FAITHFUL choice)
    run-soundness-planes.sh                     MIN_PLANES 49 -> 50 -> 51; total 74 -> 79 with --slow

`check-assigns-writes-survival` came from reading the ONE line of a byte-diff I had predicted
wrongly: `_emit_body_code` declares `#@ assigns` over **93** self-fields and emitted **29**. Module 6
builds `writes` from the emitting class's RECORD, so a field the class never DECLARED is dropped
without a word. TRAP 2989 / HOLE 0 — every dropped field is ALSO absent from the record, hence
unmentionable, hence fail-closed. That is a MEASUREMENT and not a theorem, which is why HOLE 0 is
now enforced; a HOLE is route #96's shape in a new mechanism.

## LESSONS BANKED (all in `wall-lessons.md`; (c4) and (d4) are ALSO carved into the driver skill)

  (b4b) the opaque moved the falsehood from the value to the TYPE — route #227's generator.
  (c4)  `byte-diff-compare.py` does NOT recurse: `<out>/pyref` needs its OWN invocation. I swept
        2199 files and compared none of them, and caught it only by diffing my summary line against
        gate U's, which shows TWO comparisons. **A sweep's output-directory count is not its
        comparison count.**
  (d4)  never `tail -N` a gate leg you will be asked to quote — `run-reference-tests.sh` strips the
        `(XPASS)` tag on its confirmed-FAIL re-run. What rescues you is the 0-MOVED byte-diff.
  (e4)  when a re-ported body int-erases, ask whether the mirror simply never DECLARED the field.
        #63 predicted a `\trusted` marker; it cost ONE declaration.
  (f4)  **a control you checked by GREPPING A REPORT is a claim about the report's pagination.** I
        declared a working instrument's positive control dead because I grepped a `drops[:25]` print.
        Assert a control against the DATA STRUCTURE.
  (g4)  the witness census is an AUDIT ACCELERATOR — a witnessed refusal already has an executable
        trigger, so auditing its advice is "apply the message to a file that already fails".
  (h4)  a witness that MENTIONS a refusal is not a witness that it FIRED (0415's race is a
        diagnostic; the file dies on an unjustified `#@ \diverges`). DEMONSTRATED is an upper bound.
  (i4)  **following a refusal's advice to the end is a COMPLETENESS PROBE FOR FREE** — that is how
        backlog #68 was found. The refusal has witnesses; the state AFTER the repair has none.
  (j4)  a parity plane's population is the SYNTAX it scans for, not the concept it is named after.
        `check-mirror-field-parity` walks `ClassDef` bodies, and live keeps most fields in
        `__init__` as AnnAssign-on-Attribute, so they are outside its 335 entirely.
  (o4)  **a relocation's cost is its CALLEE CLOSURE, not its line count** — a 24-line body was
        refuted by three words in one arm calling a function the destination tree does not
        have. Walk the calls; prefer a stub whose live home is itself already mirrored.
  (n4)  **a conversion's own CALL SITE can be shadowed** — converting a method creates call sites
        that did not exist while it was `\trusted`, so it can shadow a DIFFERENT already-converted
        method by giving it its first caller. Ask what the body CALLS before converting. I wrote
        (l4) one increment earlier and walked into its mirror image anyway; the plane is what
        stopped me.
  (m4)  **a detached job's `rc` is the only thing that says whether it FINISHED.** The suite's
        `rc=124` was my own timeout and I reported "still running" for four hours.
  (l4)  a conversion that FORWARDS to an undeclared callee moves trust from a counted marker to an
        UNCOUNTED abstract `val` — the count falls and the trust does not, and the vacuity planes
        pass it because nothing is erased.
  (k4)  **a value model is not a private choice of the file that adopts it — it propagates through
        the import graph as a PREAMBLE.** The emitter's "0 method stub(s)" line is about the METHODS
        crossing the boundary and says nothing about the THEORY crossing it. Count the importers
        before adopting a value model; that count is the re-proof bill.

Also sharpened: **advice naming a MARKER is the hazard when the message implies the emitter VERIFIED
something, and fine when it says the marker is an ACKNOWLEDGEMENT** (`import_classifier.py:141` is
route #90's shape and is honest). And: **an over-broad detector manufactures audit debt** — widening
the advice verbs as bare substrings claimed 173 sites where the AST census found 11, because "a list
of" and "the return value" match a bare `list|return`.

## THE LONG JOB — READ THIS BEFORE RELAUNCHING ANYTHING

`bin/run-self-annotation-suite.sh` is the authoritative "does the mirror still prove" oracle. Four
impl docs call it a gate and NO battery had ever run it before this window.

**RUN 1 DID NOT FINISH, AND THAT IS THE HEADLINE.** It ended `rc=124` — `timeout`'s exit code — at my
own twelve-hour budget, to the second, having done **25 of 40 files: 24 PASS / 1 FAIL**. It cleared
the heaviest mirrors (`module6_whyml/expressions.py`, `module6_whyml/statements.py`,
`stmt_control_flow.py`, `preamble.py`, `core_ir_semantic.py`). Its ONE failure was
`src/pycsl/errors.py`, which this generation FIXED and re-measured alone (`Verification SUCCESS`).
~~**So the oracle's honest cost is 18-24 h, not the 6-12 h the previous window estimated**~~ —
`frontend/pure_ast.py` (a measured 2.5-hour proof) and twelve other `frontend/*` files were unstarted.

> **(#49) gen #33, 2026-09-29 — RUN 2 FINISHED GREEN, SO BOTH ESTIMATES ABOVE ARE NOW SUPERSEDED BY
> A MEASUREMENT. Verified from the rc file, not from a log tail (lesson (m4)): `sas2.log.rc` = **0**
> (run 1's = **124**), tally computed by grep as **38 `[PASS]` / 0 `[FAIL]`**, and the suite's own
> line `Self-annotation: 38/38 proved`.**
>
>   * **COST: 14h31m22s** wall-clock (`SAS2 START 2026-09-28T09:44:10Z` -> `SAS2 END
>     2026-09-29T00:15:32Z`) against a 30 h budget. **Quote ~15 h at this concurrency — not 18-24 h,
>     not 6-12 h.** Both earlier figures were extrapolations from a TRUNCATED run; this one is the
>     clock.
>   * **THE MEMBER COUNT IS 38, NOT 40.** Run 1's "25 of 40" was its own truncated view, and the 40
>     has been carried forward in prose since. Another number that only a completed run could fix.
>   * `frontend/pure_ast.py` **PASSED** — the member run 1 never reached at all, and the one this
>     estimate was built around.
>   * `errors.py` **PASSED in BOTH copies** (`src/pycsl/` and `src/self-annotate/src/`), which
>     independently confirms gen #32's `as_dict` repair in the very oracle that had been red on it.
>   * **SCOPE, and it must not be overstated: the run was at commit `11ee64a7`** (its own START line
>     says so — stronger than "as of 09:44Z"), a **gen #32** commit in the frozen worktree
>     `/home/fabrice/git/pycsl-g32wt2`. **Everything gen #33 landed is OUTSIDE this verdict** — route
>     #228's refusal and its re-homing, `check-stable-hash-fold-injectivity`,
>     `check-assigns-underdeclaration`, the ratchet edits and corpus 1914/1915. A green does not
>     stand in for a tree it never saw. Re-running it is a ~15 h item for a future window; do NOT
>     relaunch it inside a battery.
>   * This is the **FIRST COMPLETE GREEN RUN of this suite in the campaign.** Four impl docs declared
>     it a gate and no battery ever ran it; window #8 scheduled it, and it now has a verdict instead
>     of an estimate.
See wall-lesson (m4): I reported "still running" for four hours after it had died, from a `ps` habit,
while my own wrapper had written the rc to disk for exactly this purpose.

**RUN 2 IS IN FLIGHT** — `<scratchpad>/g32/sas2.log`, rc written to `sas2.log.rc`, started
2026-09-28T09:44:10Z in the frozen worktree `/home/fabrice/git/pycsl-g32wt2` at **current HEAD** (not
at `1b2f676e`: the tree moved, and a verdict about the old one answers a question nobody is asking),
with `timeout 108000` (30 h). Member #1 should now PASS.
**READ `sas2.log.rc` BEFORE QUOTING ITS STATE.** If it is 124 again, the budget is still too small,
not the suite broken. If it is 0, this is the first complete run of that oracle in the project's
history and the verdict belongs in the handoff, the backlog and a commit message.

Worktrees this generation created: `pycsl-g32wt2` (run 2, LEAVE IT ALONE while alive) and
`pycsl-g32bd` (the byte-diff baseline at `c85bdb05`). `pycsl-g32wt` (run 1) is already removed.
Both remaining ones should be removed when their jobs are done.

## HAZARDS PAID FOR IN THIS GENERATION

  * `export PATH=$HOME/.opam/framac-coq8/bin:$PATH` BEFORE ANY PLANE.
  * Do NOT reuse a log path for two runs of the same battery. I overwrote a finished fast-set log with
    a second run and spent a poll cycle believing the first was hung.
  * A gate script must invoke `byte-diff-compare.py` ONCE PER EMITTED TREE and keep every leg's FULL
    log plus its `rc`. See (c4) and (d4).
  * Writing a test file into `test-suite/corpus/pycsl-reference/` while a corpus sweep is running
    corrupts the byte-diff. One advice audit had to be deferred for exactly this and then run.
  * `.claude/skills/` is GITIGNORED; the tracked copy is `config/skills/`. A skill carve-out must be
    applied to BOTH or it is invisible to the supervisor.

---

# Driver handoff — gen #31, 2026-09-25T23:50Z

Deadline **2026-09-27T08:19Z** (epoch 1790497192, written, never recomputed). Do not push.
~32 h left at the time of writing.

`$S` = `/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad/g31`

## READ THIS FIRST — the session's own conversion track failed an audit

`bin/run-soundness-planes.sh` has a FAST set (48) and a SLOW set (25, `--slow`). **Every gate
script this session ran the fast set only** — twenty-eight invocations, gates A through N, each
printing "all 48 plane(s) green". Run once with `--slow` at 21:48Z on the increment-N tree:
**5 of 73 RED**, and two of the five were conversions those same gates had banked.

SIX conversions landed this session were hollow and are now RE-TRUSTED (`d21a61fb`):

    pure_ast.py::_Parser.error                erased=['msg'] of ['msg']
    pure_ast.py::_Parser.unsupported          erased=['what'] of ['what']
    Module2_Parser.py::_ContractParser._err   erased=['msg'] of ['msg']
    monomorphize.py::_rewrite_call_sites      erased=BOTH args
    module6_whyml/identifiers.py::stable_hash erased=['s'] of ['s']
    pure_ast.py::iter_fields                  `let ... : unit`, the yielded pair dropped

Two of them had the verdict written in the file already and the converting commits left the
comment saying "STAYS trusted". See
`getting-better/open-routes/finding-eleven-gates-over-four-red-oracles.md` and wall-lesson (q6).

**RULE FROM HERE ON: a gate runs `--slow`, or it is not a verdict on a conversion.**
`bin/run-soundness-planes.sh` now says so in its own summary line (`5857acff`).

## What is running right now

| job | started | log | expect |
|---|---|---|---|
| increment-O gate (`$S/gate_o.sh`, **runs `--slow`**) | 23:44:05Z | `$S/gate_o.log` | byte-diff vs `bd_n`; mirror vs `mir_n` with FIVE declared movers; fidelity **895**; planes 73/73; suite **4029/4047**, the standing EIGHTEEN, ZERO XPASS |

## Committed since the last handoff (in order)

    60a32f79  449 -> 446 — three `pure_ast.py` dunders and a constructor
    3139c714  the whole conversion frontier, measured — 230 type errors, four walls
    85bfa846  increment N GATED — 4029/4047
    bf75103b  the FIELD value model already landed — the wall is its CLOSURE
    ff7aed38  FOUND — eleven gates over four red oracles
    d21a61fb  REVERT — six hollow conversions re-trusted, 446 -> 452
    900ff447  452 -> 451 — the string closure + `errors.py::__str__` (FOUR symbols)
    5857acff  the fast battery names its own scope
    4ff23661  progress log
    f4b495f0  route #213's two witnesses registered (a RED that predates this session)

## Standing numbers after increment O (pending the gate)

    markers                    451
    verbatim un-trusted        895
    trusted-or-dependent       828   (ratchet 828, raised 798 -> 830 naming six members,
                                      then tightened to 828 by the one conversion)
    silent-termination          56   (ratchet 56)
    untrusted-emitted          922 un-trusted, 0 `val`, 0 absent, 0 inside a trusted parent
    reasons TSV                451 rows, unclassified 442 (ratchet 442)
    emitted-vacuity            0 new erasures (9 known, gated)
    yield-erasure              0 value-erasing, 2 suspension (ratchet 2)
    shadowed-selfcalls         14 (ratchet 14), 119 bypassing sites

## The one RED still standing, and it is NOT this session's

`check-stdlib-modules-verify.py` — 104 modules, 83 verify (FAILS 6, REFUSED 13, TIMEOUT 2).
The battery truncates its stderr, so WHICH of its two failure modes fired
(`NEWLY NOT VERIFYING <module>` vs `NO-ENSURES COUNT GREW`) is NOT YET KNOWN. It is a ~25-minute
prover plane; run it alone after gate O:

    . scratchpad/g29/env.sh && python3 bin/check-stdlib-modules-verify.py 2>&1 | tail -30

**It has NOT been ruled out that the string-closure patch (`900ff447`) caused it** — the 21:48Z
battery ran with that patch already in the working tree. Gate O's own `--slow` run answers this;
if it is still RED there, bisect against `85bfa846` before doing anything else.

## Next, in order

1. Confirm gate O. If the corpus byte-diff MOVED, the string closure is not inert and must be
   re-examined before anything else — its inertness argument is that a corpus
   `if self.<strfield>:` already emits the ill-typed `<> 0` and so cannot be in a passing
   program, which is an argument, and the sweep is the measurement.
2. Resolve `check-stdlib-modules-verify` (above).
3. Re-screen the 103 markers whose recorded verdict was a `string`/`int` type error, to measure
   what the string CLOSURE actually retires: `$S/rescreen_facade.txt` (76, facade ports) and
   `$S/rescreen_differs.txt` (27, `--replace` ports). Run `$S/screen_port.sh <list>` then
   `$S/recheck_ports.sh` — NEVER trust the screen's own blacklist filter (wall-lesson: it
   scored "cannot be applied" as a pass).
4. **Every candidate that survives the screen must ALSO pass `--slow` before it is banked.**
   The four oracles that matter are `check-emitted-vacuity`, `check-yield-erasure`,
   `check-shadowed-selfcalls` and `check-untrusted-emitted`. Check 1 (the emit-diff, four
   clauses) does NOT subsume them: it admitted all six of the hollow conversions above.
5. Backlog #59 names the four capabilities that would retire those six honestly — the exception
   PAYLOAD model, the generator SEQUENCE model, the receiver-erased `.get` on a dict-typed
   parameter, and `#@ sibling_concrete` for a `NoReturn` helper.

## Discipline reminders that cost this session time

* one short step per Bash call; `timeout 43200` on every detached prover run
* never `git add -A`; never glob a directory you did not create
* kill by PID, never `pkill -f` / `pgrep -f` with a pattern that matches your own shell (c6, m6)
* check free space before `cp -a src` and delete the previous copy (a full /tmp produced a FALSE
  SOUNDNESS ALARM)
* the tracked modified `.aux`/`.olean` files under `test-suite/corpus/**/rocq|lean` are BUILD
  OUTPUT, deliberately left — do not revert or `rm` them
* `. scratchpad/g29/env.sh` sets `$S`; use a different variable name in your own scripts
