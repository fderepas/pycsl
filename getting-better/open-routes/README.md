# OPEN ROUTES — exploited, reproduced, NOT closed

## CURRENTLY OPEN: **ONE — #59.**
##
##   * **`route59-dict-assignment-is-a-value-copy.md`** — **OPEN, found 2026-09-10 (gen #4).**
##     `b = a` on a `Dict` lowers to `let b = ref !a`, a fresh ref holding a COPY, so a
##     mutation through `b` is invisible through `a`. `a[1] == 1` PROVES where CPython says
##     2. BOTH directions measured; the true twin fails, so it is a route and not a gap.
##     **The `List` carrier of the identical program is CORRECT**, which is what makes it
##     sharp: lists alias via a shared mutable array, dicts copy a pure map. Carrier census
##     DONE: broken at local->local, symmetric, chained, the FIELD carrier, and the RETURN
##     carrier (a getter handing out `self.d`); SAFE at the call boundary and, by a type
##     accident only, at `set`. **A PARTIAL repair is staged at `getting-better/staged-route59/`
##     — it closes the ALIAS carriers and does NOT close the route**, because the RETURN
##     carrier's RHS is a Call and the guard keys on a bare name or field read.
##
## (the note below predates that find and is kept for its lesson)
## PREVIOUSLY: **NONE.** Every route in this ledger is CLOSED at `cf35437f`.
##
##   #46 was the last entry still advertised as open, and it had ALREADY been closed on
##   2026-09-08 by `5f57a95d` (witnesses 1089-1091); only this file was stale. Verified
##   at HEAD by re-reproducing both halves plus four variants — see its file.
##   THREE STALE ENTRIES WERE CORRECTED IN ONE WINDOW (#56, #57, #46). The rule that
##   catches them costs one command: RE-REPRODUCE AT HEAD BEFORE BUILDING, never inherit
##   a status line.
##
##   A THIRD GENERATOR, and the structural fact behind it (gen #4, 2026-09-10):
##   **PROBE THE ORACLES, NOT ONLY THE EMITTER.** The planes that decide whether a route
##   is closed are themselves programs with defects. Ten were found and fixed in one
##   window, two of them hiding live findings — a fidelity plane that a PROSE COMMENT
##   switched off for 46 functions (one genuinely divergent), and two gates testing the
##   same `# pycsl-expected: FAIL` marker differently, which left 13 drivers required to
##   prove AND exempt from the vacuity census.
##
##   **AND THE ONE ACCIDENT WORTH KNOWING BY NAME.** Carrier censuses of routes #44/#56
##   this window found the SAME mechanism confining three of them:
##
##       LOCAL   the carrier where the routes were FOUND (the sentinel type-checks)
##       PARAM   fails closed — `Optional[T]` becomes a generated `_union_f_0` and the
##               comparison dies with "has type PyCSL_Program._union_f_0"
##       RETURN  fails closed — identically, `_union_g_0`
##       FIELD   NOT a union at all: it lowers to a plain carrier read against the
##               opaque, `if (self.v = pycsl_none)`, i.e. genuinely COVERED by the repair
##
##   So the param and return carriers of the whole `None` family are guarded by ONE Why3
##   TYPE ACCIDENT, not by four independent decisions — and a `SAFE-TYPED` verdict is an
##   accident, never a guard. **REOPENING CAPABILITY, STATED ONCE FOR THE FAMILY:** any
##   change that makes a generated `Optional` union COMPARABLE to its carrier reopens the
##   param and return carriers of #44 and #56 SIMULTANEOUSLY. That is one condition to
##   watch rather than several, and it is cheap to check — re-run the carrier probes in
##   `route56-optional-union-local-read-sentinel.md`.
##
##   An empty OPEN list is NOT a floor — it means the hunt must now GENERATE candidates
##   rather than work a queue. The two productive generators this window: probe every
##   CARRIER of a closed route (that is how #56's bool carrier and #57 were found), and
##   probe every OTHER CODE PATH that reaches the same semantics as a repair just landed
##   (that is how #58 was found, one hour after #53 closed).
##   (#53, #56 and #57 were CLOSED AND LANDED by relaunch #51 on 2026-09-10; their
##    entries below are kept as the record of how, and are marked CLOSED in place.
##    #58 was found by probing #53's OWN REPAIR for the gap it leaves.)

  * **`route58-int-truediv-is-exact-real.md`** — **CLOSED, found AND closed 2026-09-10,
    while closing #53.** int/int TRUE DIVISION keeps its own bridge, `val float_truediv_op (a b: int)
    : real ensures { result = from_int a /. from_int b }`, on a different code path from
    float-operand arithmetic (that path tests that BOTH operands are floats, so it never
    fires for `1 / 3`). It still divides over the EXACT reals, so
    **`1 / 3 > 0.3333333333333333` PROVES** while Python answers False — the two are the
    same binary64 value. Same defect as #53, one costume over.  THE COST IS DIFFERENT AND
    THAT IS WHY IT IS ITS OWN ROUTE: the fix retires `5 / 2 == 2.5`, which two NORMATIVE
    surfaces use as the headline example of the WL-02 true-division fix. THAT COST DID NOT
    MATERIALISE: folding two int LITERALS to the binary64 quotient (rendered by the same
    `repr` normalization a float literal uses, which is injective and order-preserving on
    doubles) keeps ALL of 0813 while the unsound orderings fail closed — and it RECOVERED
    `1 / 3 == 0.3333333333333333`, true of the program, which the exact-real model could
    not prove. Witnesses 1121-1124.

  * **`route56-optional-union-local-read-sentinel.md`** — **CLOSED `b9217158`** (relaunch
    #51, 2026-09-10). Kept as the record of how. The route as found: a `None`
    Optional-union LOCAL reads back as the carrier's ZERO, so `x == 0` proves where Python
    answers False, and `x + 1` proves where Python RAISES. Bounded to the `int` carrier:
    `str`/`float` fail closed on a Why3 TYPE ACCIDENT, which is exactly why routes #50/#51
    probed this class at `str` and found nothing. REPAIR BUILT AND MEASURED (route #44's
    existing `pycsl_none` opaque in the non-Some arm; no new model, ledger stays 3); it
    moves ONE mirror emission. Witnesses + landing sequence: `getting-better/staged-route56/`.

  * **`route57-dict-get-no-default-is-zero.md`** — **CLOSED `d7796dbf`** (relaunch #51,
    2026-09-10). Kept as the record of how. The route as found: **the most reachable
    route in this ledger**: `d.get(k)` on a missing key is the codomain's ZERO, not `None`.
    #56 needs an `Optional` mutable local, a shape the corpus has ZERO of; this needs
    `d.get(k)`. Decides at BOTH the `int` and `str` codomains, because `.get` picks its
    sentinel FROM the codomain type and is therefore type-correct everywhere. The zero is
    borrowed from the SUBSCRIPT read's placeholder, justified as "proven dead under
    `#@ no_exception KeyError`" — coherent for `d[k]`, which RAISES, and inapplicable to
    `.get`, which never raises. REPAIR BUILT AND MEASURED SIX WAYS (all four shapes close,
    `d.get(k, v)` still proves, the subscript path deliberately untouched); it moves SEVEN
    mirror emissions, so it owes a re-proof battery. `getting-better/staged-route57/`.

  * **`route53-float-is-a-real.md`** — **CLOSED** (relaunch #51, 2026-09-10). Kept as the
    record of how. The route as found: `τ(float) = real`, so `0.1 + 0.2 == 0.3` proves.
    Closed by ONE uninterpreted DETERMINISTIC symbol for the float arithmetic bridge, used
    by the SPEC and BODY paths alike. MEASURED cost: 2 of 916 corpus emissions, 0 of 53
    mirrors (byte-inert), and exactly ONE clause — 0517's `\result >= 0.0`, a COMPLETENESS
    loss stated in its own docstring. Witnesses 1117-1120. Repair originally decided (make the float
    arithmetic bridge a deterministic opaque and route the SPEC path through the same
    symbol); measured cost is `0517`'s non-negativity clause. The tempting refinement
    (IEEE-true SIGN clauses) is REFUTED for `*`: the clauses meet at `a = 0.0` and decide
    `r = 0.0`, but Python's `0.0 * float("inf")` is `nan`.

  * **`route46-none-branch-join.md`** — **CLOSED `5f57a95d`** (relaunch #49, 2026-09-08;
    the ledger did not record it until 2026-09-10). The route as found: route #44's
    `None` record is flow-insensitive, so a `None` bound in ONE branch of an `if` and
    something else in the other walked past it, and route #45's NaN record leaked through
    the same join. Verified dead at HEAD across both halves and four variants, with the
    TRUE truthiness fact still provable — a fail-closed fix, not a refusal blanket.
    Witnesses 1089-1091.

### THE FAMILY #44 / #56 / #57 SHARE, AND THE RULE FOR TELLING IT FROM A HARMLESS TWIN

All three are **FAITHFUL STORAGE, ERASING READ**. The model really does carry a distinct
absent value — `map 'k (option 'v)` with a genuine `None`, a variant with a real
`Arm_*_None` — and a `match … | None -> <literal>` arm throws it away AT THE POINT OF USE.
An auditor who checks the REPRESENTATION finds it faithful and concludes the class is safe.
`bin/check-collapsed-option-reads.py` (the 31st plane) now enumerates every such arm.

The rule that separates the fatal ones from the nine benign ones, written after probing all
of them: **a ghost SPEC construct may DEFINE its absent-key answer** — `\map_get(d, k)`
returns 0 for an absent key and says so on two normative surfaces — **because it is a
spec-language primitive with no Python counterpart to contradict. A BODY lowering may not**,
because there the absent value is Python's `None`.


  * **`route46-none-branch-join.md`** — route #44's `None` record is flow-insensitive, so
    a `None` bound in ONE branch of an `if` and something else in the other walks past it.
    The obvious repair (a STICKY record) was BUILT and REFUTED TWICE, both times measured;
    read that section before re-attempting it. IT NOW CARRIES TWO ROUTES' FACTS — route
    #45's NaN record leaks through the same join (`if c > 0: x = float("nan") else: x = 1`
    then `x == x` PROVES), so ONE join build closes both.

CLOSED BY RELAUNCH #48, kept here as the record of how:

  * **#42** (`<int> is True`) — `is` was given its own IR operator and the bool-singleton
    test is whitelisted. Witnesses `pycsl-reference/1053`-`1057`. `bee3564c`.
  * **#44** (`None` was the integer 0, including the CONTRACT `ensures \result == None`
    proving for a function returning 0) — a shared opaque, faithful truthiness, and a
    return-annotation-gated faithful arm. Witnesses `1058`-`1064`. `c8a58cc9`.
  * **#45** (NaN breaks the reflexivity of `==`) — an EXACT lowering, because NaN's
    comparison semantics are totally determined. Witnesses `1065`-`1069`. `49a7334a`.
  * **#47** (a `getattr` default, and the no-default form Python answers with an
    `AttributeError`, were the integer 0) — an opaque keyed on the default's IR hash.
    Witnesses `1070`-`1073`. `5342bea1`.
  * **#48** (a SEEDED `Counter`/`OrderedDict`/`defaultdict` dropped its seed and the empty
    map's missing-key default was DECIDED on) — an opaque keyed on the seed's IR hash, with
    the FACTORY form deliberately untouched. Witnesses `1076`-`1079`. `5342bea1`.
  * **#49** (in-place growth of a list PARAMETER was modelled as ABSENT, in BOTH the
    `.append` and the `+=` shape) — refused, making the mutator family consistent.
    Witnesses `1080`-`1084`. `dfa01b0d`.



The ROUTE #36 RESIDUE (`x = 0; for x in a: pass; return x`) was closed later the same
window and its reproduction moved into the corpus as `pycsl-reference/1027`. The
obstacle — a general element write-back needs the outer ref's DECLARED TYPE, which the
binder does not have — was got round by pinning BOTH types instead of guessing one: the
target is in none of the non-int local classes (so its outer ref is the integer `ref 0`
pre-declaration) AND the iterable is a formal parameter whose symbol type is `list` (so
its element is an `int`). Zero mirror emissions moved, zero corpus emissions moved,
L3-tc 53/53.

WHAT IS STILL NOT COVERED, and it is narrower than the old residue: a loop over a
NON-int sequence, or one whose target carries a non-int type. There the two types can
genuinely disagree and the binder still has no way to compare them.

Everything in this directory is CLOSED and is kept as a record of how.

---

# The original heading and entries (relaunch #45)

Everything in this directory is a **live unsoundness with a working reproduction**.
Each file PROVES a contract that is FALSE of its own program, at HEAD, in the DEFAULT
`hoare` memory model, with no flags. They are kept HERE rather than in
`test-suite/corpus/pycsl-reference/` for one reason: a corpus witness for an open route
would be an **XPASS**, which the harness has counted as a failure since relaunch #44.
Move each file into the corpus in the SAME increment that closes its route.

## ROUTE #35 — CLOSED (relaunch #45, later the same window). Kept for the record.

The obstacle described below was real and the fix that overcame it is in
`module6_whyml/expressions.py`: separate PYTHON-BOOLISHNESS (does `1`/`0` already
encode the Python value faithfully?) from WHY3 TYPING (may this operand be selected
raw, or must it be wrapped back to an int?). `left_b == f"({left} <> 0)"` is the
precise second test. Mirror L3-tc came back 53/53, sixteen mirror emissions moved,
and their re-proofs were run. Witnesses are now `pycsl-reference/1023`-`1024`.

### The original entry, unedited:

## ROUTE #35 — `and`/`or` in a VALUE position return a boolean, not the operand

    x = 0 or 5      # Python: 5     model: 1
    x = 3 and 7     # Python: 7     model: 1

`module6_whyml/expressions.py`, the `raw_op in ("and","or")` branch, ends in
`return f"(if {left_b} {op} {right_b} then 1 else 0)"` under a comment that says "In
body context, Python's and/or return int". They return an OPERAND. The lowering is
CORRECT IN A CONDITION and WRONG IN A VALUE, and nothing at the emission site knows
which consumer it has. The string-operand and emit_ir-operand cases immediately above
it ALREADY select the operand — the general case never caught up.

REPRODUCTIONS: `route35-shortcircuit-value.py` (false, proves) and
`route35-shortcircuit-value-faithful.py` (true, does not prove).

### Why it is not closed here, MEASURED rather than guessed

* The value-preserving form
  `(let __or_l = <l> in if __or_l <> 0 then __or_l else <r>)` moves **19 of the 53
  mirror emissions**, including `expressions.py` (20125 goals, ~4h),
  `frontend/pure_ast`, `Module5_IREmitter`, `statements`, `stmt_control_flow`,
  `Module6_WhyMLTranspiler` and `preamble`. That is 19 whole-file re-proofs.
* AND THE NAIVE FORM IS ILL-TYPED. `_to_bool` returns a Why3 **bool** from many of its
  branches (a comparison, `Array.length … <> 0`, `hval_truthy …`, `py_isinstance_…_op`,
  an inductive predicate) and an **int** from exactly one (`({x} <> 0)`, its default).
  Selecting on the raw operand therefore emits `bool <> 0`: measured, the first version
  took mirror L3-tc from 53/53 to **40/53**, and the spike proof
  `frontend/module_collect` failed with "This expression has type bool, but is expected
  to have type int".
* PYTHON-BOOLISHNESS AND WHY3 TYPING ARE DIFFERENT QUESTIONS and the fix needs both:
  the first decides whether the `1`/`0` encoding is already faithful (it is, for a
  chain of comparisons — Python returns `True`/`False` there and `1`/`0` encodes it
  exactly, which is what keeps the ordinary `a == b or c == d` shape byte-inert); the
  second decides whether an operand may be selected raw or must be wrapped with
  `(if <bool> then 1 else 0)`. `left_b == f"({left} <> 0)"` is the precise test for the
  second. A THIRD trap is already documented in the code: the boolishness test must
  RECURSE through nested `and`/`or`, or `a == 0 and b == 3 and c == 1` looks like
  "int on the left, bool on the right" — the first version refused six real corpus
  files (0290, 0900, 0901, 0935, python-reference 0158/0161) because of it.

### The capability, named

Reconcile the two tests as above, then pay the 19 re-proofs. Estimated 8-12h wall at
two concurrent proofs. This is a COST/SCALE boundary in the §A.3 sense, not a
correctness one — every piece is expressible and the obstacles are enumerated here.

## ROUTE #36 — CLOSED for the index-valued loop (relaunch #45). Kept for the record.

The refusal described below was the wrong instrument and the entry stands as a record of
why. What landed instead is a WRITE-BACK in the binder: assign the OUTER ref immediately
before opening the inner `let`. It reproduces Python exactly, never-ran case included, it
is scoped to targets the function reads outside their loop AND to index-valued loops
(where the bound term is the counter and is int-typed like the outer ref), and it moves
**zero** mirror emissions and **zero** corpus emissions — so it cost no re-proofs at all,
against the fourteen the refusal implied. Witnesses `pycsl-reference/1025`-`1026`.

RESIDUE, recorded rather than hidden: `for x in <sequence>` followed by a read of `x`
still yields the pre-loop value. A general element write-back is NOT well-typed — the
outer ref takes its type from the FIRST assignment to that name, which need not be the
loop's element type. Measured: an unconditional write-back took mirror L3-tc to 51/53
(`expressions.py`, `functions.py`) and an `any int` havoc to 52/53 (`stmt_control_flow.py`,
whose loop target ref is `emit_ir`). Closing the residue needs the outer ref's declared
type at the binder, which it does not have.

### The original entry, unedited:

## ROUTE #36 — the `for` loop variable does not survive the loop

    i = 0
    for i in range(3):
        pass
    return i        # Python: 2      model: 0

The body opens `let i = ref (!_idx_i) in` INSIDE the loop, so the name is shadowed and
the OUTER `i` still holds its pre-loop value afterwards. Python leaves a loop variable
bound to its LAST value.

REPRODUCTIONS: `route36-loop-var-leak.py` (target pre-assigned) and
`route36-loop-var-leak-no-preassign.py` — BOTH prove. The second matters: a first guess
was that the exploit needs a stale pre-loop value, and it does not, because Module 6
declares the loop target as an outer `ref 0` regardless.

### Why it is not closed here, MEASURED rather than guessed

A pipeline-level REFUSAL of "the `for` target is read outside its loop" is written and
kept in `route36-refusal-that-broke-14-mirrors.py.txt`. It works, and it **breaks the
self-annotation mirror**: 14 of the 53 mirror files stop emitting, because reading a
loop variable after its loop is an ordinary Python idiom the emitter itself uses
throughout. A gate that makes the tool unable to verify itself is not shippable, and
exempting the mirror from its own soundness check is exactly the move this campaign
refuses.

One narrowing was tried and rejected on evidence: "refuse only when the target is
ASSIGNED before the loop" leaves `route36-loop-var-leak-no-preassign.py` exploitable.

One EXCLUSION in that refusal is worth keeping in any future version: a Python `assert`
is DROPPED by Module 6 (measured on `python-reference/0177`, whose `assert i == 5`
after a `break` loop emits nothing at all), so a read inside one is not a leak — and
counting it fails a PASSING corpus test for no soundness gain.

### The capability, named

Bind the OUTER ref in the loop body (`i := !_idx_i`, or `i := <elem_expr>` for a
non-range iterable) instead of shadowing it. That reproduces Python exactly INCLUDING
the never-ran case, where the variable keeps its previous value. It moves every
for-loop emission that reads its target afterwards — the same 14 mirror files — so it
carries the same 14 whole-file re-proofs. Do it in the same funded increment as #35;
the two overlap heavily in the files they touch.

---

## THE STRING MODEL'S BOUNDARY, MAPPED (gen #4, 2026-09-10) — PROBED, NO FINDING

Ten probes, every one run in BOTH directions, because "fails closed" without its true twin
does not distinguish a MODEL from a REFUSAL — the check route #53's file was caught having
skipped.

    MODELLED (false claim FAILS, true twin PROVES):
      len("abc") == 3          true -> PROVES        len("abc") == 4     false -> fails
      "abc" == "abc"           true -> PROVES        "abc" == "abd"      false -> fails

    OPAQUE — fails closed in BOTH directions, i.e. a COMPLETENESS GAP, not a guard:
      "a" < "b"                true -> FAILS         "b" < "a"           false -> fails
      "ab" + "cd" == "abcd"    true -> FAILS         ... == "abcd_"      false -> fails
      "abc"[0] == "a"          true -> FAILS         "abc"[0] == "b"     false -> fails

So string EQUALITY and LENGTH are genuinely decided, while string ORDERING, CONCATENATION
and INDEXING are uninterpreted. That is the safe configuration and there is no route here.
It also explains the previously recorded gap `"abc"[10:20] == ""` (true, does not prove):
slicing sits on the same opaque side as indexing, and is not a separate defect.

**REOPENING CAPABILITY — the thing to check if anyone makes these concrete.** Ordering,
concatenation and indexing are exactly the operations a completeness pass would want to
implement, and they are currently safe BECAUSE they are uninterpreted. Anyone giving them
a concrete model must re-run the FALSE column above in the same change: string ordering in
particular is where route #53's twin defect would live, since a concrete order on a hashed
or truncated string representation decides comparisons Python answers the other way.

**DO NOT RE-PROBE THESE TEN.**

---

## SIGNED `//` AND `%` ARE FAITHFUL IN ALL FOUR QUADRANTS (gen #4) — PROBED, NO FINDING

The highest-yield place to look for a route in any Python verifier, because Python FLOORS
toward negative infinity while C and most SMT integer theories TRUNCATE toward zero, and
`%` takes the sign of the DIVISOR rather than the dividend. Nine probes, both directions.

    python: -7//2 = -4   -7%2 = 1   7//-2 = -4   7%-2 = -1

      -7 // 2 == -4   (Python, true)  -> PROVES      -7 // 2 == -3  (C, false)  -> fails
      -7 %  2 ==  1   (Python, true)  -> PROVES      -7 %  2 == -1  (C, false)  -> fails
       7 // -2 == -4  (Python, true)  -> PROVES       7 // -2 == -3 (C, false)  -> fails
       7 %  -2 == -1  (Python, true)  -> PROVES       7 %  -2 ==  1 (C, false)  -> fails

**MODELLED, not merely refused, in every quadrant** — each C-semantics claim fails AND each
Python-semantics twin proves. This is a genuinely reassuring result rather than an absence
of evidence, and it is only meaningful because both columns were run.

Gen #3 had probed `5 // 0` and `5 % 0` (both fail closed). NEGATIVE OPERANDS were not
covered by that, which is why this was worth doing: division by zero and division by a
negative are different code paths reaching the same operator, and "a repair covers the PATH
it edits" cuts both ways when deciding what has actually been checked.

One completeness gap alongside it, recorded rather than left loose:

      (-2) ** 3 == -8   TRUE of the program  ->  does not prove

which sits with the already-recorded `2 ** -1 == 0`: exponentiation is opaque outside the
simple positive cases. Safe direction, no route.

**DO NOT RE-PROBE THESE NINE.**
