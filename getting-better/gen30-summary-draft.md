# gen #30 — SUMMARY (finalised at the deadline, §A.3; 2026-09-23T07:59Z)

**Branch** `ghost-assign-bc6`. Nothing pushed; pushing stays gated to the user.

---

## §A.3 SUMMARY — the four things the skill asks for

**ROUTES RESOLVED.** Twenty-nine SEV-1 routes demonstrated (#191–#218): **twenty-five
CLOSED** with a refusal or a faithful lowering, each carrying an expected-FAIL witness and
a PASS control, and **four OPEN** (#212, #213, #214, #218) — demonstrated, priced, and left
open deliberately because every candidate repair was measured and found worse than the
defect, or (for #218, found in the window's last two hours) because the obvious refusal
lands on ANOTHER ROUTE'S WITNESS and verifying that consequence did not fit. All four have
carriers outside the corpus and a plane that runs them; it reports 4 carriers, all
reproducing.

**ROUTE #218 CORRECTS A CLAIM THIS CAMPAIGN MADE IN ITS OWN CORPUS.** A dunder declaring
`#@ assigns self.v` and setting it is emitted as `val c___enter___0 (self: c) : int` with
NO `writes`, and **Why3 reads a `val` with no `writes` as PURE** — so a caller reading the
field either side of an explicit `c.__enter__()` PROVES IT UNCHANGED (`\result == 0`) while
CPython answers -7, and the TRUE twin FAILS. Witness 1800 had recorded the dunder drop as
"SOUND, NOT UNSOUND: ... the caller can prove LESS, never more". That is true about the
RESULT and false about the FRAME: a contractless `val` is fresh in what it returns and PURE
in what it writes, and purity is a POSITIVE claim about the whole heap. The witness's
docstring now carries the correction. `PYCSL-CONTRADICTORY-ASSIGNS` names this exact hazard
in its own message and does not fire, because it refuses stubs whose clauses CONFLICT and
this stub's clauses never reach the emitter — lesson (t3), for the third time in one night.

**ROUTE #216 WAS FOUND BY CHASING AN UNDEMONSTRATED REFUSAL, on the last night.** Two files
identical except for ONE IDENTIFIER, under `--check-behavioral-subtyping`: `Sub.m` returning
0 against `Base.m`'s `\result >= 5` FAILS, with `goal sub__m_refines_base` in the emission.
Rename `m` to `__len__` and it reports **"All contracts formally proven"** over a module
whose entire body is `type sub = {  }` — no methods, no override pair, NO GOAL. `#@
conforms_to` has the same hole through a different recorder. It is route #97's family (the
substitutability obligation never recorded, so never checked) with a new trigger, and the
guard written for #97 misses it because **it covers "recorded but unresolvable" and not
"never recorded"**. Blast radius measured: ZERO existing dunder override pairs anywhere in
the repository, so it is LATENT — which is the argument for writing it down, not against:
`__len__`, `__eq__` and `__lt__` are the first methods a real user overrides. **CLOSED the
same night** by `PYCSL-SEM-DUNDER-OVERRIDE-UNCHECKED` at the `_run_pipeline` choke point
(a `\trusted` twin: no marker, no mirror edit, no re-proof), gated on the flag so no
default run changes: witnesses 1805/1806, controls 1807 (a dunder with no override still
PASSES) and 1808 (the same violation spelled `m` still FAILS), plus two negative controls
by hand. What it does NOT buy is a CHECKED dunder override — that needs dunders emitted,
which is the same work witness 1800 waits on, and the route file says so.

**ROUTE #215 CAME OUT OF THE ADVICE AUDIT, WHICH IS THE POINT OF THE AUDIT.** Following
monomorphize's GT4 advice ("the recursive call must use a concrete type") produced a file
that would not verify; isolating with controls — a generic CLASS verifies, a NON-generic
function verifies, a generic FUNCTION does not — showed the call lowering to `(any int)`.
Probing that erasure gave a false contract PROVING: `a = ident[int](1); x = a;
a = ident[int](2); return x - a` proved `\result == 0`, because the per-NAME erased
constant is not refreshed on REBINDING. And the ground truth is sharper than the first
draft of this sentence: `ident[int](1)` is NOT VALID PYTHON — PEP 695 makes a generic CLASS
subscriptable but a generic FUNCTION is not, and CPython 3.14 raises `TypeError`. The model
was proving a postcondition about a program that cannot run. REFUSED at `_run_pipeline` (a
`\trusted` twin, so no marker and no re-proof), blast radius measured first at 2 corpus
occurrences and ZERO in the mirror, the live tree and `pycsl_lib`; witness 1796, control
1797.

**ROUTE #217 CAME OUT OF PRICING THE HANDOFF'S OWN "FULL DAY" ITEM, AND IT COST FORTY
MINUTES.** `b = bytes([1, 2, 3]); b[0] = 9; return b[0]` PROVED `\result == 9` while CPython
raises `TypeError: 'bytes' object does not support item assignment`. `PYCSL-SEM-SUBSCRIPT`
already carried the perfect refusal and never saw the local: it keys on the symbol table
typing the local `"bytes"`, and only a bare bytes LITERAL got that classification — the
CONSTRUCTOR form stayed `"Any"`. Witness 1725 pins the COUNT form and calls this gap
"pre-existing and separate"; the ITERABLE form, eight of the nine corpus sites, had NO
witness at all. Closed by one branch in `_build_function_symbol_table`, whose mirror twin
is `\trusted` (no mirror edit, no re-proof — the expensive part the estimate assumed).
**Whole-corpus byte-diff, both sides emitted fresh: 1303 baseline, 0 MOVED, 0 APPEARED,
exactly 1 GONE** — witness 1725 itself, expected-FAIL either way, now failing BY THE
REFUSAL instead of by the ill-typedness its own docstring flags as an accident doing the
enforcing. The same comparison covers route #216, so that refusal is byte-verified inert
too. And a guess in the handoff was CHECKED AND IS WRONG: typing the iterable form does not
make reads more faithful — all five surviving emissions are byte-identical.

**CONVERSIONS AND THE COUNT DELTA.** `\trusted` markers: **459 → 459. ZERO conversions.**
That is the honest headline, and the generation's answer to it is not an excuse but three
measurements that say what 459 does not mean: 56%–61% of the mirror is trusted OR
trust-dependent (`check-trust-blast-radius`), only 15% of the un-trusted mirror says
anything about the VALUE it computes (`check-mirror-claim-strength`), and **45%** of the
corpus carries a contract that says nothing at all (1791 of 3973, and the detector was
audited and came back clean) (`check-claim-vacuity`). One marker was
attacked directly — `hlib.Sha256.update`, the layer's one BARE `\trusted` — and proved
FORCED, so the measurement went into the marker and the gate now enforces a `reviewer:`
clause at zero.

**THE EVENING STRETCH (20:30–23:40Z) — SIX ARTIFACTS IN ONE INSTRUMENT, SEVEN FALSE
STDLIB CONTRACTS, AND THE ADVICE SURFACE CLOSED.** Two debts the handoff had priced turned out to be worth more than
their price, in opposite directions.

*The 24 UNADJUDICATED identity stubs* were all adjudicated against this CPython, and
**seven carried a contract FALSE of the function their own header cites**: `csvmod.write_row`
(`writerow(['a','b','c'])` returns 7, the CHARACTER count, not 3 fields — and its own
docstring said so), `cvar.context_var_get` / `context_var_set`, `dec.getcontext_prec`
(unguarded above `decimal.MAX_PREC`, where the assignment RAISES), `nums.rational_num` /
`rational_den` (`Fraction(2,4).numerator` is 1 — `num >= 0`/`den > 0` do not imply
coprimality), and `csvmod.writerows`. **Two of them were PROVED downstream** in
`src/pycsl_lib_test/`, which is the route standard met inside the stdlib layer. SIX ARE
NOW REPAIRED and re-verified; the seventh (`que.qsize`) turned out innocent on
investigation and is reclassified, not fixed. The pass needed two new classes
(DECLARED-DOMAIN, MODEL-INTERNAL) with `pkl.dump` as the standing control that stays OUT
of the first. `MAX_UNADJUDICATED` 24 → 0. A NEW PLANE came out of it —
`check-docstring-contract-disagreement.py`, the free oracle: a docstring that states a
weaker relation than the clause beside it, four of its five hits deliberate CONTROLS.

*The 113 refusals with no witness*, priced at "five minutes each" — nine hours of corpus
files — **was an instrument artifact FIVE times over.** (1) 318 of the census's 437
refusal rows were cut at 110 characters by a writer three generations old. (2) Eight
`validate_ir` checks are not reachable from a `.py` source at all. (3) Nine raises have no
literal of 25 characters, so their fragment is empty and no witness can ever match. (4)
Several raises use `%s` formatting, so the AST literal contains placeholders the compiler
never prints — three real witnesses fired and moved the count by ZERO. (5) One row was cut
MID-UTF-8, leaving a replacement character, and the file proving that refusal
(`1265_w68_hs_foreign_receiver_call.py`) had sat in the corpus for three generations.
(6) And the worst: the walk required the RAISED NAME to start with `PyCSL`, so the
twenty-one raises that import their exception class under a LOCAL ALIAS — **every route
refusal this campaign has landed in `pycsl.py` since route #29** — were not in the
population at all. 198 sites became 219. The
instrument was repaired in four conservative passes plus two guards, and now **REFUSES**
rather than report a number when its own inputs are unusable. **85 → 184 demonstrated,
113 → 17 undemonstrated**, with all 219 sites partitioned for the first time (184 + 17 +
8 not-source-reachable + 10 unmatchable). (It ends the generation at **191 of 220**, 6
undemonstrated — see the bullet further down; the numbers here are where the evening
stretch left it.) Twenty-five witnesses were written along the way —
and four more were written, confirmed to fire, and DELETED as redundant.

**THE ADVICE SURFACE, MEASURED FOR THE FIRST TIME AND CLOSED.**
`getting-better/convergence-metric-implement.md` has listed it as unmeasured for
generations: *"62 advice-bearing messages, and #90 came from one. No metric ... samples
English prose for exploitability; the advice-audit generator remains manual."* A refusal's
advice is a CLAIM THE COMPILER MAKES ABOUT ITSELF, in the one place a user is guaranteed to
read, and it was the only claim in the system with no gate behind it. **All 108 have now
had their advice FOLLOWED AND RUN** — a file written the way each message says, compiled,
verdict recorded — in the new plane `bin/check-refusal-advice-audited.py`. **102 work.**
The six that did not were all REPAIRED the same evening and fail in four distinct ways:
UNSPELLABLE (`#@ shared`, `#@ touches_field` — a directive named without its argument, and
a reader types what is inside the backticks); UNTRIED (an explicitly-called DUNDER does not
carry its contract; `Optional[List[T]]` emits unbound `array` — **twice the compiler told a
user to write a program it cannot compile**); AMBIGUOUS (one repair needs an unstated LOCAL
instance; one OR-list's first disjunct is really a conjunction with the second). **Route
#215 came out of this audit**, and so did two standing completeness findings nothing else
in the repo measures.

**LESSONS BANKED.** **Twenty-seven** new entries in `getting-better/wall-lessons.md` — ten
from the route work (v2–e3) and **seventeen from the final stretch (f3–v3), all of them about
INSTRUMENTS**, which is the honest shape of this generation. The last five were banked in
the closing hours and each came from a gate, or a sentence, catching its own author: (r3) a gate whose
INPUTS can be deleted underneath it must REFUSE, not crash; (s3) "it was refused" is not
the claim, "it was refused FOR THIS REASON" is; (t3) a guard written for a defect covers
the case you HAD, not the case you can HAVE — ask what never ENTERS the collection it
iterates; (u3) the choke point is a property of the FUNCTION, not of the FILE;
(v3) re-read the SOUNDNESS ARGUMENT your own witness makes, AS A CLAIM — the half of it
that is missing is usually about the FRAME, and route #218 is that missing half. The full list with worked
examples is in that file's index; the route half reads: (v2) an
unmentioned exclusion is an oversight wearing one; (w2) attack a marker before believing
it is forced; (x2) trust has a blast radius and a PASS count is not a proof count; (y2) an
enforcement mechanism that writes into a body is only as strong as the guarantee the body
is compiled; (z2) a check with no witness has no evidence it can fire; (a3) "verify the
dependency" is not "verify the file"; (b3) a lowering fix must re-run the refusal the old
shape was accidentally enforcing; (c3) read the axiom registry the way you read the
docstrings; (d3) a repo has FOUR populations that must keep working and a refusal measured
on two has been measured on the easy two; (e3) when a measurement fails under load, re-run
it quiet before you explain it; (f3) an exclusion you never tested is a guess; (g3) a
docstring that disagrees with the contract beside it is a free oracle; (h3) a new class
only earns its place if it comes with a CONTROL that stays out of it; (i3) an absence
claimed from an instrument that could not have shown the presence is not a measurement —
banked because I recorded a residual that was itself FALSE and the correction is kept
beside it; (j3) a coverage gate can be measuring its own artifact, and **a number that
RECOMMENDS EFFORT deserves the scrutiny of one that reports success**; (k3) four artifacts
in one instrument is a fact about the instrument, and the fix is a SELF-AUDIT, not a
fourth patch.

**UNPUSHED COMMITS.** See the final line of the run summary; nothing was pushed, and
pushing stays gated to the user.

---

## Routes (SEV-1, each with the decisive signature: a false contract PROVING while the TRUE twin is REFUSED, and CPython run as ground truth)

**TWENTY-FIVE CLOSED (#191–#217 less the three open ones) and THREE OPEN (#212, #213,
#214), every one demonstrated with a false contract PROVING while CPython disagrees** —
with route #215's ground truth sharper still: CPython cannot RUN the program at all
(`TypeError: 'function' object is not subscriptable`), so the model was proving a
postcondition about a program that does not exist. An
open route here means the defect is demonstrated and the repair is PRICED — not that it
was left unexamined; each one's doc says exactly what blocks it.

| # | what the model claimed | where |
|---|---|---|
| 191 | a `None` stored anywhere read back as the integer 0 | `expressions._expr_to_whyml`, the typed `NoneExpr` leaf |
| 192 | a genuine integer 0 was re-tagged as `None` at an `Optional`/union parameter | the two lifts that recognised `None` BY THE SPELLING `"0"` |
| 193 | the placeholder array for an unrepresentable iterable had a KNOWN LENGTH | `_array_coerce_arg`, the `"0"` arm |
| 194 | an erased collection was the integer 0, and an int-erased param's contract read it | `_coerce_to_int`, the array/map arms |
| 195 | the empty-list placeholder was the integer 0 at an int-erased param | `_coerce_dotted_args` |
| 196 | the empty-list placeholder was 1024 elements long at an `array int` param | `_coerce_dotted_args` |
| 197 | `getattr(o, "a", 0)` on an UNKNOWN-typed object answered the DEFAULT and the body read it | `expressions`, the getattr fall-through |
| 198 | a BARE `return` was the integer 0 | `stmt_control_flow._handle_return_stmt` |
| 199 | the EMPTY f-string `f""` was the integer 0 | `expressions._handle_fstring_expr` |
| 200 | a string literal actual was HASHED into a declared `int` param, and the hash ships in this repo | `_coerce_dotted_args` -> `_coerce_to_int` |
| 201 | a string actual became a ONE-ELEMENT array at a `List[int]` param | `_array_coerce_arg`, the TAIL |
| 202 | the same hash through an UN-ANNOTATED param, and through the KEYWORD slot | the #200 refusal's own two blind spots |
| 203 | a SINGLE-part f-string `f"{n}"` was the integer it interpolates | `expressions._handle_fstring_expr`, the int-model joiner |
| 204 | an `#@ interface assigns` NARROWER than the definition — the importer framed the call with it | `functions._emit_narrowing_vc` proves `ensures` and `requires` and emits nothing for `assigns` |
| 205 | an over-claiming `#@ interface ensures` was refused AT HOME and believed by EVERY importer | the narrowing VC was "emitted only in the owning unit" |
| 206 | a `happy … total` availability policy proved over a target whose helper is a `\trusted` `while True` | `Module3_Weaver`, route #93's check covered the TARGET only |
| 207 | `no_exception \all` proved through a `\trusted` METHOD that always raises | route #161's method arm, admitted on the strength of a name |
| 208 | the same `total` policy through a `\diverges` helper — through MY OWN #206 repair, 20 minutes later | the callee set was derived from the witness, not from the rule |
| 209 | the `protects` trust boundary asked a `pure_ast` matcher about a CSL node and had NEVER fired | `Module3_Weaver`, R1.1 |
| 210 | a `#@ check False` stamped into a `\trusted` body that is never lowered | the `protects` form's site loop |
| 211 | the same inert stamp in the PARAMETRIC (`footprint`) form; the twin is one annotation line | the R3 site loop |
| **212** | **OPEN** — the importing unit believes EVERY contract of an imported module: frames, postconditions, class invariants | nothing checks the module was verified; `--verify-imports` built, off by default |
| **213** | **OPEN** — two reads of the same `getattr` are ONE per-site constant across a call that writes the attribute | the refusal was landed and REVERTED: 212 live / 14 mirror functions use the idiom |
| **214** | **OPEN** — two reads on DIFFERENT unknown receivers share route #47's default-keyed constant and are EQUAL | the faithful repair breaks corpus 1073; blocked on local-type inference |
| 215 | `a = ident[int](1); x = a; a = ident[int](2); return x - a` proved `\result == 0` — and `ident[int](...)` is NOT VALID PYTHON: CPython raises `TypeError: 'function' object is not subscriptable` | the unresolved generic call erased to a per-NAME opaque constant that REBINDING does not refresh; refused at the `_run_pipeline` choke point |
| 216 | `Sub.__len__` refining `Base.__len__` reported **All contracts formally proven** with NO override pair and NO goal, over a module whose whole body is `type sub = {  }` — CPython answers 0 against a promised `>= 5` | the DUNDER drop reaching BOTH obligation recorders (`ir_resolve.apply_inheritance` and `Module5_IREmitter`'s `#@ conforms_to`); refused at the `_run_pipeline` choke point |
| 217 | `b = bytes([1,2,3]); b[0] = 9; return b[0]` proved `\result == 9` — CPython raises `TypeError: 'bytes' object does not support item assignment` | `_build_function_symbol_table` typed a `bytes(...)`-CONSTRUCTOR local `"Any"`, so `PYCSL-SEM-SUBSCRIPT`'s immutability guard never saw the local it was written for |

## The second half of the generation (2026-09-22, 14:30-15:30Z) — EIGHT more routes in one stretch

Every one came from the same move: **read a justification as a checkable claim, then ask
which SPELLING it did not run.** Three of them came from ONE sentence
(`_emit_narrowing_vc`'s docstring), and four are one defect wearing four hats:

>>> A `#@ happy` POLICY ENFORCES ITSELF BY INJECTING A CHECK INTO A BODY, AND A `\trusted`
>>> BODY IS NEVER LOWERED, SO THE INJECTION EVAPORATES.

`bin/check-happy-trust-boundaries.py` now runs a CARRIER and a CONTROL for each boundary
through the shipping pipeline (3.2 seconds for ten programs, because a refusal precedes the
prover). It is executable on purpose: #209 and #211 both READ correctly in the source and
could not fire.

**#208 is the generation's sharpest lesson about itself.** It walked through my own #206
repair twenty minutes after that repair landed, because I derived the refusal's callee set
from HOW #206's witness happened to be written (bodyless) instead of from WHAT the rule
means (no termination VC). The campaign's own lesson (i) — *name which spellings were run* —
missed on my own patch, inside the hour.

### Three measurements that reframe the campaign's own numbers

None is a soundness failure. All three are the gap between what a number SAYS and what a
reader HEARS, which is the same defect class as a false contract, one level up in the prose.

| measured | number |
|---|---|
| corpus files that run with `--no-proof` (a PASS means the pipeline did not crash) | **1754 of 3881 — 45%**, and 38 of a 40-file sample VERIFY under the prover |
| corpus files whose contract says NOTHING (`ensures True`) | **1792 of 3888 — 46%**, including ALL 840 `*_call_fails.py` AND ALL 840 `*_call_proves.py`; 60 of 60 sampled `*_call_fails.py` VERIFY under full proof |
| the UN-trusted mirror that makes a VALUE claim | **143 of 933 — 15%** (624 carry only a frame claim, 166 no clause at all) |
| the mirror that is trusted OR trust-dependent | **56%-61%**, against a headline marker count of 459 |

## Planes added or collected

**THE LAST NIGHT ADDED TWO MORE, both out of reading the undemonstrated-refusal list — and
one MECHANISM that is not a plane:**

* `bin/lib_plane_lock.py` + a lock in `bin/run-soundness-planes.sh`. Five planes EMIT
  `.mlw` beside the mirror or corpus sources and others READ them in place; the battery's
  loop is sequential exactly so they never overlap, and a hand-run from another shell
  defeats that. **It happened three times in one night, to the driver who had just written
  the lesson about it** — once producing a traceback and a spurious RED in a 67-plane run.
  A rule a careful driver breaks three times in one night is a rule that needs a mechanism.
  Fail-open for the battery, fail-closed for the hand-run; stale locks ignored; all four
  behaviours verified by running them.

**THE LAST NIGHT ADDED TWO MORE, both out of reading the undemonstrated-refusal list:**

* `bin/check-frontend-ir-backstop-refusals.py` — five front-end / lowering BACKSTOPS
  demonstrated EXECUTABLY, each with a well-formed control that must be accepted. Four of
  them (`PYCSL-SEM-SPAN`, `PYCSL-TY3-CALLABLE-SHAPE` ×2, `PYCSL-IR-OPAQUESTMT`) fire on
  shapes the FRONT-END itself builds, so no `.py` file can reach them: they were never
  seventeen unwritten witnesses. Coverage 17 → 13 undemonstrated, ceiling lowered with it.
* `bin/check-emitted-function-coverage.py` — **did the FUNCTION reach the module at all?**
  912 corpus files compared, 1 zero-coverage, 5 partial, and EVERY dropped function in the
  entire corpus is a DUNDER. That partition is the ratchet; a non-dunder drop refuses. It
  is the plane route #216 needed, and its matcher took THREE repairs (a `let lemma`, a
  `py_` prefix, and the `with` of a mutually-recursive group) each of which removed a FALSE
  positive — the third would have opened the plane with a red that was entirely mine.

**THE FINAL STRETCH ADDED THREE, and two of them measure a surface nothing measured before:**

* `bin/check-refusal-advice-audited.py` — **the ADVICE surface.** A refusal's advice is a
  claim the compiler makes about itself, in the one place a user is guaranteed to read, and
  it was the only claim in the system with no gate behind it (`convergence-metric-implement.md`
  has listed it as unmeasured for generations). All **108 of 108** audited by WRITING THE
  PROGRAM EACH MESSAGE DESCRIBES and running it; 102 work, and the six that did not were all
  repaired. Route #215 came out of this audit. Keyed on a 140-character text signature
  (measured: 64 collides 8 times) PLUS a whole-message hash, because the key looks at the
  message's start and the advice lives at its END.
* `bin/check-ir-schema-refusals.py` — the eight `validate_ir` structural refusals,
  demonstrated EXECUTABLY because no corpus witness can reach them. A grep for `validate_ir`
  across `test-suite/` found ZERO: the IR's own structural contract had no test of any kind.
  Eight malformed-IR carriers, a WELL-FORMED control, and a #44 guard that refuses on a
  rename or a new uncarried check.
* `bin/check-docstring-contract-disagreement.py` — the FREE ORACLE: a `pycsl_lib` docstring
  that states a WEAKER relation than the `#@ ensures \result ==` clause beside it. Built
  because two of the seven false stdlib contracts had already said so in their own prose.
  Four of its five standing hits are CONTROLS.

* `bin/check-argument-coercion.py` — every argument substitution classified PASS-THROUGH vs SUBSTITUTION, with a justification each.
* `bin/check-proof-reverify.sh` — the axiom-footprint gate. Its ratchet was driven **6 -> 0** (VERIFIED 155 -> 166: eleven `#@ proof` axiom imports nothing had ever checked).
* `bin/check-trusted-reasons.py` — a full plane that existed and **nothing ran it**; collected into the runner.
* `bin/check-return-boundary-substitutions.py` — the RETURN side, the gap `check-argument-coercion.py` names in its own header and `check-constant-fallthrough.py` names in its own. Pins occurrence COUNTS, and was demonstrated to fire on the pre-#198 tree via `--live`.
* `bin/check-corpus-contract-truth.py` — the value-differential's method (curate nothing,
  re-run CPython every pass) applied to BOTH REFERENCE CORPORA instead of to 75 curated
  drivers. **379** PASS-expected files across `pycsl-reference` and `python-reference`
  already carry a zero-arg function with a literal `#@ ensures \result == N`: **367 AGREE
  with CPython, 0 DISAGREE**, 12 unrunnable (a category — programs CPython
  cannot run, because they name `#@ datatype` types). That is FIVE TIMES the curated
  population, at no cost in drivers written. A failure here is the sharpest verdict the
  battery can give: a test that passes the prover while its own postcondition is false of
  its own program. There are none.
* `bin/check-coercion-exits.py` — the trigger rule's THIRD firing: `_array_coerce_arg` (#193, #201) and `_coerce_to_int` (#194, #200/#202) each produced two routes, and `check-argument-coercion.py` classifies the call SITES without ever looking inside the helpers. Pins both exit sets with counts; demonstrated to fire on the true pre-#201 source.
* `bin/check-fstring-lowering.py` — built because the campaign's own trigger rule fired: TWO routes (#199, #203) in ONE function in ONE session. Pins the return set with counts AND two structural tokens, because #203 added a *wrap* rather than an exit and the return-set half is green on the pre-#203 tree — a blind spot the `--live` self-test found before it shipped.

Battery: **18 -> 39 fast planes** (49 with `--slow` at the mid-generation mark; the slow set grows with the fast one), and `MIN_PLANES` tightened from a floor that carried slack to the exact count. The second half added eleven more, listed below.
`check-swallowed-exceptions` ratchet **4 -> 0**, a hard zero.
Five new `value-differential` drivers (v73-v77), the CPython-measured plane, covering
#198, #199 and #203 in both the DISAGREE and the AGREE direction.

## Battery evidence

**FINAL STRETCH (2026-09-22 evening → 2026-09-23):**

* Fast planes (mid-stretch): **43 of 43 GREEN** at HEAD 95ba418b, after every compiler edit of the
  evening — three refusal-message repairs, route #215's refusal, the union-array late
  pull — and the three new planes. MIN_PLANES 40 → 43.
* Mirror re-proof of `src/self-annotate/src/core_ir_semantic.py`: **all contracts formally
  proven**. It was owed because `_check_mutable_defaults` is one of the 887 VERBATIM
  un-trusted twins and its refusal message changed twice; the evening's other three
  message repairs sat in `\trusted` twins and owed nothing, which is the choke-point rule
  earning its keep.
* Mirror-sync **887 verbatim** and mirror-coverage **549 / 41** unmoved by any of it.
* `check-stdlib-modules-verify` full run: 104 modules, **84 VERIFY**, 20 do not
  (FAILS 5, REFUSED 13, TIMEOUT 2) — and of the 84, ONE has value-returning functions with
  no `#@ ensures` and SEVEN have no value-returning function at all, so the honest headline
  is **76**.
* **THE CORPUS BYTE-DIFF FOR THE FINAL STRETCH IS NOW SWEPT, AND IT IS ZERO IN ALL THREE
  DIRECTIONS.** Both sides emitted fresh — baseline `86b6287a` in a worktree (1301 corpus
  `.mlw`), candidate HEAD (1303) — and `bin/byte-diff-compare.py` reports **0 MOVED, 0
  GONE (0 unexpected), 0 APPEARED**, with 2 new source files correctly ignored via the
  `SOURCES.txt` manifest. APPEARED is the direction that matters most and is the one an
  ad-hoc diff-the-common-files loop cannot see: a REFUSAL THAT BECAME AN EMISSION, which
  is how route #42 reopened under a green "byte-diff ZERO over 887". The paragraph below
  was the argument this sweep was owed against, and it is kept verbatim because the
  argument turned out to be RIGHT — which is not the same as having been CHECKED:

* **(superseded by the sweep above, kept for the record) THE CORPUS BYTE-DIFF FOR THE FINAL
  STRETCH IS ARGUED, NOT SWEPT, AND THAT DISTINCTION IS STATED DELIBERATELY.** Three of the four emitter edits are refusal-MESSAGE text, which
  appears only in a refusal and never in emitted WhyML. The fourth and fifth are each gated
  on a construct MEASURED ABSENT from the corpus: route #215's refusal fires only on
  `f[T](...)` over a generic function (2 corpus occurrences, both in expected-FAIL files),
  and the union-array late pull fires only when a union arm is an `array` (ZERO corpus
  files use `Optional`/`Union` over any container spelling). That is a strong argument and
  it is not a sweep: the sweep is a handoff item, because **"byte-inert by construction" is
  the claim this campaign has twice caught itself making without checking.**
* TWO gates went RED because of witnesses written the same evening, and BOTH were fixed at
  the source or by a NAMED exemption, never at the ratchet: `check-claim-vacuity`
  (`requires True` copied into four new witnesses — deleted) and `check-dropped-mutation`
  (CTXBIND, because witness 1784 IS a `with ... as` — named in `CTXBIND_EXEMPT`, exactly as
  1759 was named in `DANGLING_EXEMPT`).

* **AND THE GENERATION ENDS WITH `[+] soundness-planes: OK — all 69 plane(s) green.`** —
  twice, the second time at `e6e5e53f`, covering every change made after the first. It is
  the same battery that ended 8 RED the first time it was run honestly. At that same tree:
  fast planes 44/44; corpus byte-diff **1306/1306, 0 MOVED, 0 GONE, 0 APPEARED**;
  clause-survival 4 deficits all EXPLAINED, 0 unexplained; emitted-function-coverage 8
  dropped functions, **0 non-dunder**; trusted-frame-honesty 0 model-visible of 1 and of
  94; open-route-carriers 4 of 4 reproducing; mirror-sync 887 verbatim. The headline metric
  was re-measured by RUNNING it rather than recalling it:
  `markers 459 · attached 459 · unattached 0`.

* **THE FIRST FULL `--slow` BATTERY OF THE GENERATION (67 planes) ENDED 8 RED, AND THREE
  OF THE EIGHT WERE REAL — TWO OF THOSE THREE WERE CAUSED BY ME, THAT EVENING, AND NEITHER
  WAS VISIBLE IN THE EDIT THAT CAUSED IT.** That sentence is the argument for the battery.
  * Five REDs were `why3` not being on PATH. Every one was a CORRECT per-plane refusal
    (rc=2) and every one was spurious as a statement about the tree; all five pass with
    `. scratchpad/g29/env.sh`. `--slow` now checks `command -v why3` at second zero and
    REFUSES with the one-line instruction, instead of spending forty minutes producing a
    summary known in advance to be wrong about five planes. The per-plane guards stay as
    the backstop.
  * `check-trusted-frame-honesty` rc=1, "RATCHET BROKEN — 2 > 1": the union-array repair
    made `_emit_union_arm_vc` write `self._needs_union_array_use` while its mirror
    `\trusted` stub still declared `#@ assigns \nothing`. A `\trusted` frame is ASSUMED,
    never checked — so that is not a stale annotation, it is a false assumption every
    proof downstream rests on. The stub now declares the write; the ratchet was NOT
    raised (rule (k)).
  * `check-emitted-vacuity` rc=1, a TRACEBACK on a `.mlw` that `os.walk` had just listed.
    I had run an emitting plane BY HAND while the battery ran, and it moved the file out
    from under the plane that reads it in place. The battery's loop is sequential exactly
    so that cannot happen. Lesson (r3); the plane now REFUSES naming the file, because a
    gate measuring a moving target has no verdict and a traceback reads as "the gate is
    broken" when the truth is "the measurement is void". Re-run alone: green, no new
    erasure.
  * `check-clause-survival` rc=1, 3 deficits against a ratchet of 2 — see below.

* **CLAUSE-SURVIVAL STOPPED COUNTING AND STARTED EXPLAINING.** The third deficit was the
  evening's own witness 1800, whose deficit IS the file's subject. Raising 2 to 3 would
  have been rule (k), so the count stopped being the gate: every deficit file must now
  NAME the def whose disappearance explains it, and the plane confirms that mechanically
  (the def exists in source, is ABSENT from the emission by exact `__`-suffix match on
  emitted idents — so the dunder's contractless call site `val c___enter___0` does not
  count as the method being emitted — and carries enough clauses to cover the shortfall).
  `MAX_UNEXPLAINED = 0` is strictly stronger than "at most 3 files, cause unknown". Two
  self-tests show it can refuse. **And the classification said what the count could not:
  all three deficits are ONE phenomenon — a method the emitter drops takes its contract
  with it** (0661/0662 a constructor's nineteen `requires`, 1800 a dunder's single
  `ensures`). Measured: 912 compared, 3 deficits, 3 EXPLAINED, 0 UNEXPLAINED.

* Suite at `bc0561ec` (#198/#199/#200 + the return-boundary plane): **3823 / 3841**, 746
  XFAIL, **0 XPASS**, and the SAME 18 CONFIRMED FAIL this campaign has carried.
* Corpus byte-diff: ZERO pre-existing programs moved for every one of #198-#203.
* Mirror emission byte-diff: ZERO for #199/#200/#202/#203; exactly ONE file for #198 and
  ONE for #201, each the edited method's own mirror, each a one-line diff that is exactly
  the intended correction (M1).
* Fast planes: green after each of #198, #199, #200, #201, #202 and #203 (22/22, then
  23/23, then 24/24 as the last two planes were added).
* **Both moved mirrors RE-PROVED**: `module6_whyml/stmt_control_flow` (#198) —
  `Verification SUCCESS`, 12589 prover results; `module6_whyml/expressions` (#201) —
  `Verification SUCCESS`, **21347** prover results. M1 satisfied in both: the diff was
  exactly the intended correction AND the affected program re-proves.
* **gen11 differential fuzzer**: 60/60 seeds, **960 programs across the RETURN boundary**,
  ZERO false proofs — the honest negative for the boundary that produced #198.
* **gen12** (the STRING/INT representation boundary, where #199/#200/#202/#203 all live):
  40/40 seeds, **800 programs, ZERO false proofs**. With gen11 that is **1760 differential
  programs across the two boundaries this generation repaired**, finding nothing after the
  repairs.
* **gen13** (the STORE-AND-READ-BACK boundary, route #191's archetype generalised to
  fourteen store/read pairs): 560 programs, running.

### The third stretch (17:00-18:00Z) — mining the axiom registry, and acting on a plane

* **ROUTE #213 (OPEN)** — route #197's own sentence ("two reads of the SAME `getattr`
  expression agree") read as a claim. Sound only while the attribute cannot change: with
  honest frames, `x = getattr(o,"a"); mutate(o); y = getattr(o,"a"); return x - y` PROVED
  `== 0` where CPython answers -98. My refusal missed the THREE-ARGUMENT spelling (the
  second time in one day) — and then the refusal itself was REVERTED, because its
  blast-radius census covered the corpus and `src/pycsl_lib` and not the MIRROR or the
  LIVE TREE, where 14 and 212 functions respectively read the same `getattr` twice with an
  intervening call. The mirror stopped emitting (44 of 53) and four planes went red. Both
  carriers now live outside the corpus under `check-open-route-carriers.py`.
* **ROUTE #214 (OPEN)** — the other arm: `getattr(o,"a",{})` and `getattr(p,"b",{})` on
  two different unknown receivers share route #47's default-keyed constant and are EQUAL.
  Both repairs measured and blocked; `bin/check-open-route-carriers.py` now runs the
  carrier, because an open route's carrier cannot be a corpus witness.
* **A `stable_hash` COLLISION, constructed** — `"ah02"` and `"atc3"` both fold to
  185314078 after 24,726 strings. Three paths probed; none exploitable today, because the
  one op that receives a folded literal is a `val`, not a `val function`. That is ONE
  KEYWORD of margin, so `bin/check-hashed-literal-purity.py` now holds it.
* **THE AXIOM REGISTRY DISAGREES WITH ITSELF** — every `Pycsl.Struct.Std.round_trip_*` is
  range-guarded "faithful to CPython's out-of-range struct.error"; the legacy
  `UnixFs.Struct.{i1a1,i2,i18}` are not, and citing one proves a `>HH` round-trip for
  70000 that CPython refuses to pack.
* **`capwords` NEVER GROWS A STRING — except it does.** The imported axiom's own comment
  justifies itself with "capitalize (first upper, rest lower; LENGTH-PRESERVING)".
  `string.capwords('ß')` is `'Ss'`, 1 → 2. The Rocq and Lean proofs are honest about their
  `list Z` model; the defect is the faithfulness of `capwords_def`, which that comment
  names as the trusted core. Four gate improvements came out of it, and the gate STILL
  cannot fire, because the model encodes the default separator as `sep == ""` while
  CPython's default is `None` and `capwords(s, "")` raises.
* **58 OF 198 REFUSALS HAD A WITNESS.** `bin/check-refusal-witness-coverage.py` joins the
  compiler's raise sites against a census of all 759 expected-FAIL witnesses (404 refusals,
  355 verification failures, **0 XPASS**). Then twelve witnesses were WRITTEN — Final
  F1/F2, three lemma arms, two assigns-region arms, `\length` on a dict, `\result` in a
  check, two `happy` name typos, `d.items()` in a contract — taking it to **68/198**, and
  both ratchets moved with the measurement.

* **AND BY THE END OF THE GENERATION IT IS 191 OF 220, WITH THE REMAINDER PARTITIONED
  RATHER THAN CALLED A DEBT:** 191 DEMONSTRATED, **6** undemonstrated, 13 NOT REACHABLE
  from a `.py` source (each demonstrated executably by a direct gate, with a well-formed
  control), 10 UNMATCHABLE by this instrument. Every one of those four numbers is a
  measurement:
  * the 13 were found by READING the undemonstrated list one by one instead of treating it
    as N unwritten witnesses — four fire on shapes Module 5 itself builds, one is an API
    parameter (`pure_ast.parse(type_comments=True)`) no source file can set;
  * the 10 stay 10 because the obvious widening (a regex from all literal runs joined by
    `.*`) was PROTOTYPED over the whole census and would move exactly ONE site — both
    `Module1_Ingestor` empty-body raises share the 13-character "`: empty body", so no
    threshold can tell them apart;
  * and the census stopped rotting: `--append-new` runs only the witnesses with no row,
    through the same helper as `--regenerate`, because the two-hour refresh is exactly the
    pressure that makes someone hand-edit a TSV — **and a hand-written census row is a
    measurement nobody made**. It found FOURTEEN uncensused witnesses, four of them from
    before this evening.
  * The most user-visible refusal in the system — `"PyCSL Syntax Error around line"` —
    turned out to have NEVER BEEN SEEN TO FIRE: zero of 841 censused rows contained it,
    because every corpus contract is well-formed by construction. Witness 1813.

### Planes added in the second half (37 -> 39 fast)

* `bin/check-stdlib-identity-stubs.py` — the `return <param>` family: **81 stubs pinned by
  their own contract, 23 of them FALSE of the function their header cites**, only six of
  which the calling gate could ever reach.
* `bin/check-stub-import-resolution.py` — measures the sentence two other gates rest on.
  TRUSTED_STUB resolves NOTHING, and nine package names would shadow the real module the
  day the glob is repaired.
* `bin/check-corpus-contract-truth-args.py` — the parameterized half of the corpus oracle:
  412 functions, **4354 argument-level evaluations, 0 disagreements**, and the exclusions
  that produced the 45% / 46% numbers.
* `bin/check-trust-blast-radius.py` — 56%–61% of the mirror is trusted or trust-dependent.
* `bin/check-claim-vacuity.py` — the SECOND vacuity: **1791 of 3973** corpus files say nothing (the denominator grew with this generation's own witnesses; the numerator did not, which is the ratchet working). Its detector was AUDITED at the end of the generation and came back CLEAN: two broader syntactic families — `ensures A <op> A` for identical text, and `ensures <lit> <op> <lit>` for every comparison — scanned over all 3973 files found ZERO additional hits, so the number is not an undercount hiding behind a narrow regex. The operator set was widened anyway, and what stays invisible (SEMANTIC tautologies, which need the expression evaluator) is now named in the plane.
* `bin/check-mirror-claim-strength.py` — 15% of the un-trusted mirror makes a value claim.
* `bin/check-trusted-termination-honesty.py` — the third honesty plane (frame, raises, and
  now TERMINATION): 52 trusted bodies whose termination is assumed and unverified.
* `bin/check-happy-trust-boundaries.py` — an EXECUTABLE gate for all six `#@ happy` trust
  boundaries, carrier and control, 3.2 seconds.
* `bin/check-refusal-witness-coverage.py` — which of the compiler's 195 raise sites has a
  witness DEMONSTRATING it can fire (static half in; the two-hour census is the artifact).
* `bin/check-stdlib-modules-verify.py` — does the stdlib layer verify at all? (SLOW; the
  first measurement is 83 of 104, and the TCB appendix's own `os` example is among the 21.)
* collected, not written: `core-only-conformance.py`, `frontend-only-conformance.py`
  (already run by the suite — a correction recorded in the ledger) and
  `os-cpython-differential.py`, a CPython differential oracle for the `os` exception model
  that cost 0.1s and that nothing ran.

## The method, in one sentence

Read a plane's — or a function's — OWN WRITTEN JUSTIFICATION as a checkable claim, and probe
it by giving the callee a contract that is TRUE OF ITS OWN BODY and that READS the property
the substitution changes. A callee with `ensures True` hides the entire family, which is why
the call boundary survived 190 routes.

## Lessons banked this generation

(a)-(g) from the first half; (h) difficulty is not soundness; (i) name which SPELLINGS were
run; (j) predict the TRUE twin, and give completeness its own witness; (k) the choke-point
rule is enforced by two ratchets; (l) build the plane the other planes named; (m) a repair
that fixes one arm leaves the rest of the function; (n) a residue you write down is a work
item; (o) the lesson you just banked applies to the fix you just shipped; (p) the upper bound is not the blast radius — read the arm, then count that shape; (q) a
gate built from a route must be run against the pre-route tree; (r2) `timeout` forwards its
signal to its child, so kill the wrapper; (u2) when a plane's method is "run the real
thing", the scope is a SAFETY property; (v2) an unmentioned exclusion is not an exclusion,
it is an oversight wearing one — READ YOUR OWN GATE HEADERS THE DAY AFTER YOU WRITE THEM;
(w2) a marker that looks lazy may be FORCED: attack it, measure what stops you, and bank
the measurement IN the marker; (x2) trust has a BLAST RADIUS, and a PASS count is not a
proof count; (y2) an enforcement mechanism that writes into a body is only as strong as the
guarantee that the body is COMPILED — enumerate every way a subject can fail to be
compiled; (z2) a check with no witness has no evidence that it can FIRE, and "the sibling
form has a witness" is not evidence about this one; (a3) a module can be meaningful only
inside an importing context, so a module-level certificate is not "this file verifies on
its own".

**THE FINAL STRETCH ADDED FIFTEEN MORE, AND THEY ARE ABOUT INSTRUMENTS** — (f3) an exclusion
you never tested is a guess, so re-derive the reason when you copy it forward; (g3) a
docstring that disagrees with the contract beside it is a FREE ORACLE; (h3) a new class
only earns its place if it comes with a CONTROL that stays out of it; (i3) an absence
claimed from an instrument that could not have shown the presence is not a measurement
(banked because I recorded a residual that was itself FALSE); (j3) a coverage gate can be
measuring its own artifact, and **a number that RECOMMENDS EFFORT deserves the scrutiny of
one that reports success** — and the bound was documented, it just died in the queue;
(k3) four artifacts in one instrument is a fact about the instrument, and the fix is a
SELF-AUDIT, not a fourth patch; (l3) a single number invites over-reading, a BRACKET or a
PARTITION does not; (m3) a refusal's ADVICE is a claim the compiler makes about itself and
nothing tests it — **a refusal offering two repairs should have had BOTH tried**; (n3) a
new refusal can RETIRE an old one by running first, so look for what STOPS firing; (o3)
when new evidence does not move a number, suspect the number's COLLECTOR — its population
filter most likely excludes the work this campaign is busy adding; (p3) a class boundary
drawn from a STATIC READING is a hypothesis, and the discipline is **print the members
before you write a ceiling**; (q3) a staleness key must cover the part the verdict is
ABOUT, not merely be stable; (r3) **a gate whose INPUTS can be deleted underneath it must
REFUSE, not crash** — of the three endings available when a file vanishes mid-read,
silently skipping it is a green over a shrunken population and a traceback reads as "the
gate is broken" when the truth is "the measurement is void", so the #44 rule points one
level lower: a gate must be able to tell "I looked at all of it" from "I looked at what
was still there"; (s3) **"it was refused" is not the claim, "it was refused FOR THIS
REASON" is** — a gate whose oracle is "the compiler refused this" must pin WHICH refusal,
or it cannot tell a working guard from a neighbouring guard, or from a typo (two of the
six `#@ happy` boundaries were green for the wrong reason, one of them on a SYNTAX ERROR
in a policy the grammar does not have); (t3) **a guard written for a defect covers the
case you HAD, not the case you can HAVE** — `PYCSL-SUBTYPING-PAIR` names route #97's
hazard exactly and still misses route #216, because it covers "recorded but unresolvable"
and #216 is "never recorded", so for every `for x in COLLECTION: if bad(x): refuse`, ask
what stops an x from reaching COLLECTION at all; (u3) **the choke point is a property of
the FUNCTION, not of the FILE** — twice in one night an edit was priced as expensive
because its FILE is a mirrored un-trusted twin, and both times the FUNCTION's twin was
`\trusted`, so it owed no mirror copy and no re-proof: forty minutes against a day, and a
cost estimate written without that one check reads later exactly like a cost that was
measured; (v3) **re-read the SOUNDNESS ARGUMENT your own witness makes, as a claim** —
witness 1800's "a contractless `val` ... lets the caller prove LESS, never more" was true
about the RESULT and silent about the FRAME, and the missing half is route #218: for every
soundness argument about a CALL, say what it claims about the result and what it claims
about the frame, SEPARATELY.

## A surface opened this generation: the `pycsl_lib` stdlib layer

93 body-verified stub packages, governed by `config/skills/agent-stdlib-annotate`, with
**no gate in the 24-plane battery comparing a stub against the module it stands in for.**
Two instruments were built and run for the first time:

* `scratchpad/g30/stdlib_diff.py` — BODY differential. Its headline (129 "mismatches") is
  misleading and that is the finding: the stubs are ABSTRACTIONS, not re-implementations,
  so body equality is the wrong criterion. The control proves the harness works: `bsect`,
  the one package that IS a faithful re-implementation, matched `bisect` on 8000 inputs.
* `scratchpad/g30/stdlib_contract_diff.py` — CONTRACT differential, the right criterion:
  generate inputs satisfying `#@ requires`, run the REAL module, evaluate `#@ ensures`
  against CPython's answer. 2000 checks, **21 violations in 2 functions** —
  `mth.remainder` (claims `\result >= 0`; `math.remainder(8,5)` is `-2.0`) and
  `stat.filemode` (claims the constant `"----------"`; the real one returns `'?-------w-'`).

**Severity checked, not assumed, and downgraded:** `import_classifier._stub_set` reads only
the `.py` stems directly under `src/pycsl_lib/`, and no name map takes `math` to `mth`, so
nothing substitutes these contracts for a real stdlib import.

**AND THEN THAT SENTENCE WAS ITSELF MEASURED** (`bin/check-stub-import-resolution.py`, the
30th plane). It is true today and for a SECOND reason nobody had stated: the lookup globs
top-level `*.py` while the layer ships 93 PACKAGES, so the live stub set is `{"__init__"}`
and **TRUSTED_STUB resolves NOTHING AT ALL** — the layer was renamed from a flat
`data/lib_stubs/` and the glob was never renamed with it. What does NOT survive a repair:
**nine package names were never renamed under the `mth` convention and ARE real stdlib
module names — `copyreg`, `errno`, `http`, `json`, `os`, `re`, `reprlib`, `stat`,
`token`.** On the day someone fixes that glob — a one-line, obviously-correct-looking
change — `import os`, `import json` and `import re` in USER code resolve to this layer, and
11 pinned facades plus 8 identity stubs stop being claims about a model and become claims
about the world. The gate holds all four facts (live stub set, package floor, collision
ratchet, exposed-contract counts) and self-tests by pointing the walk at a layer that DOES
ship `os.py`.

The defects the two instruments found are therefore documentation and naming defects in
standalone modules, not live unsoundnesses. The number that survives: **124 of 870 `pycsl_lib`
functions (14.3%) have a single-constant-return body** — harmless while nothing consumes
them as stdlib models, and exactly what becomes a hole on the day something does.

**AND THEN IT WAS BUILT**: `bin/check-stdlib-contract-fidelity.py`, the 26th fast plane.
The map is derived from the stubs' OWN headers (50 of the 93 name an importable stdlib
module) and restricted to 24 PURE, DETERMINISTIC modules — the exclusion is a SAFETY
property, since the gate calls the real function with generated arguments and `shutil`,
`subprocess`, `tempfile`, `os`, `io`, `signal` and `pathlib` are all in the header-derived
set. **5202 contract evaluations, 6 baselined divergences** — the two real defects above
plus four `csys` functions whose own header declares the 0..1000 integer scaling. It is
deterministic (fixed pools, no randomness — a sampling gate cannot carry a ratchet), guarded
at 4500 evaluations, and self-tested: `--selftest-empty-baseline` must exit 1, and does.

**It was widened TWICE more the same generation, each time from a finding rather than a
plan**: to 34 modules when re-deriving the headers showed thirteen safe ones simply
unlisted (six new diverging stubs, all of the identity family), and to 35 when
`strmod.capwords`'s false length bound turned up in the axiom registry. With `\str_length`
taught to the translator and `==>` split at paren depth zero, it now runs **5612
evaluations against 12 baselined divergences** — and the header records the four
exclusions (`csv`, `tokenize`, `linecache`, `glob`: filesystem hazards; `sysconfig`:
per-install paths) that were previously just absent.

A SECOND stdlib plane followed, because the first one could not reach the sharpest set:
`bin/check-stdlib-pinned-facades.py` (the 27th). The differential gate CALLS the real
function, so `os` is on its safety deny-list — and `os` holds ten of the twelve functions
whose body is a single constant AND whose contract PINS that constant. That gate is pure
AST: **870 functions scanned, 12 facades baselined by name**, `os.islink -> 0` the sharpest
(a proof that nothing is ever a symlink). One entry is faithful and baselined anyway
(`sysmod.get_float_info_max_10_exp -> 308` is the right answer) because **the gate keys on
shape, not on truth**, and the baseline says so rather than leaving the next reader to
re-derive it.

Two documentation defects were also FIXED this session, both emission-byte-identical:
`mth.remainder` lost the false sentence "For integers, same as x % y" (IEEE rounds to
nearest, `%` floors), and `stat.filemode` was relabelled a ten-character placeholder with
the faithful fix PRICED (ten independent bit tests over a string model with no
per-character theory).

A THIRD stdlib plane followed from a question the first two provoked: does the campaign's
own headline metric reach this layer? **It does not.**
`bin/count-trusted-directives.py` globs `MIRROR/**/*.py` and `bin/check-trusted-reasons.py`
scopes to `src/self-annotate/src`, so the **459 marker count excludes `src/pycsl_lib/`
entirely** — and that layer carries two markers, one of them a BARE `#@ \trusted` with no
reviewer and no reason (`hlib.Sha256.update`, in a class whose `hexdigest` returns
`[0] * 64`). The skill for that layer says it carries ZERO trusted markers and that an
opaque kernel becomes an abstract `val` pinned by a cited `#@ proof`, never `\trusted`.
**The rule existed, the violation existed, and no plane connected them.**
`bin/check-stdlib-trusted-markers.py` (the 28th) now does, with the bare marker baselined
and its defect named rather than failed on arrival.

>>> A METRIC THAT DOES NOT REACH A DIRECTORY IS NOT A METRIC FOR THAT DIRECTORY.

What remains for the `agent-stdlib-annotate` owner is the judgement the gates deliberately
do not make: whether to give those twelve facades real bodies or weaker contracts, and
whether `hlib.Sha256.update`'s trust becomes a reviewer clause or an abstract `val`.

## Standing, deliberately deferred (re-priced this generation, not inherited)

* `check-avatar-frame-parity` (B) INHERITED segment: **7 sites, not 11**, none pre-stubbed —
  7 new markers plus a 5-6 iteration caller fixpoint over five mirrors, one at 8250s/proof.
* the hval absent-key sentinel's MIRROR side, left honestly OPEN with the next step named.
* **ROUTE #218's repair**, deferred by ninety minutes rather than by cost: the remaining
  judgement is whether refusing an explicit self-writing dunder call is right for
  `python-reference/0076.py`, a different suite with different rules, and two of the three
  measurements that got to that single file were wrong on the first try. Repair 2 — emit
  the `writes` the `#@ assigns` already declares — is named as the one to price first.
* **EMIT DUNDERS**, which is the single change that would close route #216's remaining
  half (the obligation is refused, not CHECKED), route #218, witness 1800's gap and the one
  zero-coverage file in `check-emitted-function-coverage`. Byte-diff-RISKY:
  authorize-first, and it is item 1 in the handoff.
* the `bytes` COUNT-form lowering (`Array.make n 0`, as `bytearray` already has) — route
  #217's refusal now holds the line, so the type error is no longer load-bearing, which
  was the precondition the old note named.
* **witness 1804's shape**: `a: list = []` rebound to a literal in a branch emits an
  UNDECLARED `a_len` AND an always-true `Array.length a <> 0` truthiness test, so route
  #31's archetype is blocked only by a type error. A refusal was PRICED AND DECLINED — 6
  mirror and 32 live functions share the shape and a blanket refusal breaks the mirror,
  which is route #213's mistake. The faithful fix is to declare the counter AND test
  `!a_len <> 0`; 1804 is the tripwire until then.
* **`check-proof-reverify.sh` dirties 13 TRACKED `.aux` files** on every `--slow` run. That
  is the trap behind this generation's near-miss, where tidying them by glob deleted
  several hundred tracked files. Recompile into a temp directory, or untrack them.

## CONVERSIONS: ZERO, AND THAT IS THE HONEST HEADLINE

The base self-tcb-reduction loop's metric is `\trusted` stubs CONVERTED to verified
methods, and this generation converted **none**: the count stands at **459**, exactly where
it started. What the window did instead was close **twenty-five SEV-1 unsoundnesses**, add **ELEVEN new
plane files** (counted, not recalled: `git log --diff-filter=A -- 'bin/check-*.py'` since
the generation baseline) and take the registered fast battery from **24 to 44**, with the
`--slow` set at **69 and ALL GREEN** for the first time in the generation — the difference
being planes that already existed and were being run by NOTHING. Those are not
a substitute for conversions; they are the other half of the same job.

**AND THE FINAL STRETCH ADDS A THIRD THING THE METRIC DOES NOT SEE.** Six distinct
artifacts were found and fixed in ONE instrument (`check-refusal-witness-coverage`), the
ADVICE surface was audited end to end for the first time (108 of 108, six broken messages
repaired), and three headline numbers were corrected downward because they were being read
as more than they said. None of that converts a marker. All of it changes what the campaign
KNOWS — and the 113-refusal work item it retired was priced at nine hours against a number
that was wrong by a factor of six.

>>> A GENERATION SPENT FIXING ITS OWN INSTRUMENTS LOOKS LIKE A GENERATION THAT DID NOTHING,
>>> ON A METRIC THAT COUNTS MARKERS. The honest accounting is that the measurements this
>>> campaign steers by were wrong in six distinguishable ways, and are now right. A converted stub reduces what the verifier ASSUMES; a closed route fixes what
the verifier CLAIMS. A tree with 459 markers and no false proofs is in a better place than
one with 400 markers and six live routes, and the campaign's own rule — never re-baseline a
gate to make it green — is the same instinct applied to the metric: **do not convert a stub
while the emitter under it is still proving things that are false.**

Stated plainly so the next window can disagree with it: if the route yield drops, the
conversion track is where the budget should go, and the two deferred segments
(`check-avatar-frame-parity` (B), the hval absent-key mirror side) are priced and waiting.

## Metrics at the end of this session (measured, not recalled)

| metric | value | note |
|---|---|---|
| `\trusted` markers | **459** | unchanged across all six routes landed after the third kill — every repair was placed so it cost no marker |
| unmirrored live defs | **549** / 1823 (30.1%) | the mirror-coverage ratchet, unmoved (the two ratchets that caught #200's first placement) |
| `\trusted` stubs whose live body raises | 76, of which **62 SILENT** | a named ratchet, unmoved; reducing it moves callers' VCs and is a segment, not an increment |
| broad swallowing handlers that FIRE | **0** | driven 4 -> 0 this session; the baseline is now an empty set, a hard zero |
| axiom-footprint UNRESOLVED | **0** | driven 6 -> 0 earlier in the generation (VERIFIED 155 -> 166) |
| fast planes | **44** | MIN_PLANES tightened to the exact count each time it moved (40 -> 43 -> 44) |
| planes with `--slow` | **69** | and the first ALL-GREEN `--slow` run of the generation, with `. scratchpad/g29/env.sh` sourced; `--slow` now REFUSES up front when why3 is off PATH instead of printing five spurious REDs forty minutes later |
| corpus | **1736** in `pycsl-reference`, **3994** total | +53 in the final stretch (1762-1814); 845 expected-FAIL witnesses censused, every one of them with a census row (`--append-new` found fourteen that had none, four from before the evening) |
| refusal coverage | **191 of 220** demonstrated | a partition: 191 + 6 undemonstrated + 13 not-source-reachable + 10 unmatchable-BY-MEASUREMENT (the widening was prototyped and moves exactly one). Began the evening reported as 85 of 198 |
| advice-bearing refusals AUDITED | **108 of 108** | 102 FOLLOWABLE; the six broken ones all repaired. A surface `convergence-metric-implement.md` had listed as unmeasured for generations |
| stdlib identity stubs UNADJUDICATED | **0** (was 24) | and SEVEN of the 24 were false of the function they cite; six repaired |
| stdlib modules verifying WITH a postcondition | **76** of 104 | the honest reading of "84 of 104 verify": of the 84, one has value-returning functions and no `#@ ensures` and seven have no value-returning function at all |
| value-differential drivers | **75** | +5 earlier this session (v73-v77) |
| corpus byte-diff, whole generation's final stretch | **0 MOVED · 0 GONE · 0 APPEARED** | MEASURED, not argued: baseline `86b6287a` in a worktree against HEAD, both sides emitted fresh, 1301 vs 1303 `.mlw`; and again after routes #216/#217 (1303 -> 1302, the single GONE being witness 1725's intended new refusal) and after the composition fix (1306/1306, all three zero) |
| unpushed commits | see `git log origin/ghost-assign-bc6..HEAD` | **nothing pushed; pushing stays gated to the user** |

**AND THE METRICS THAT MOVED MOST WERE INSTRUMENTS, NOT THE COMPILER.** Refusal coverage
went 85 -> 184 with only 31 witnesses written: the rest came from repairing the CENSUS
(truncated at 110 characters by a writer three generations old, and again mid-UTF-8), the
MATCHER (a `%s` placeholder the compiler never prints), and the POPULATION FILTER (21
raises invisible because the campaign's own route refusals import their exception class
under an alias). "84 of 104 stdlib modules verify" is worth 75. "81 identity stubs" had 78
more of the same shape beside it. "113 refusals need witnesses, five minutes each" was 19.

>>> Six distinct artifacts in ONE instrument in one evening, and the tell was the same
>>> every time: A WITNESS THAT FIRED AND MOVED NOTHING. Banked as (j3), (k3), (l3), (o3).

**The metric that did not move is the point.** Thirteen SEV-1 routes were closed this
generation without adding a single `\trusted` marker and without moving the coverage or
raises-honesty ratchets: every repair was either an opaque inside an already-effectful
method, a faithful value, or a refusal placed at a choke point whose mirror is already
trusted. Two planes (`check-mirror-coverage`, `check-trusted-raises-honesty`) enforce that,
and they caught the one placement that would have broken it.
