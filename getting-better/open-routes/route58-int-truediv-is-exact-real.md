# ROUTE #58 — **CLOSED** 2026-09-10 by relaunch #51 (generation #3), the same window
# that found it. int/int TRUE DIVISION WAS AN EXACT REAL DIVISION, SO IT DECIDED A
# COMPARISON PYTHON ANSWERS THE OTHER WAY.
#
# ## HOW IT WAS CLOSED — AND IT IS BETTER IN ALL THREE DIRECTIONS, NOT A TRADE
#
# TWO INT LITERALS ARE FOLDED exactly as CPython folds them, and rendered through the
# SAME normalization the float-literal leaf uses (`repr` of the binary64 value, or
# `<int>.0` when integral). EVERY OTHER OPERAND SHAPE — a parameter, a local, a call —
# goes to one UNINTERPRETED DETERMINISTIC `val function float_truediv_op (a b: int)
# : real`, spec path and body path alike.
#
# WHY FOLDING IS SOUND rather than the same bug at a finer scale, which was the
# make-or-break question: the shortest round-trip `repr` is INJECTIVE on doubles and
# ORDER-PRESERVING (two distinct doubles differ by at least one ulp, so their half-ulp
# rounding intervals are disjoint), and a float LITERAL in the source goes through the
# IDENTICAL normalization — measured: `0.10000000000000001` emits as `0.1`. So a folded
# quotient and a literal compare in the model exactly as the two doubles compare in
# Python. Had literals been emitted verbatim, folding would have been unsound and the
# design would have had to change.
#
# THE OUTCOME, all measured:
#   * the UNSOUNDNESS closes  — 1121 (literal) and 1122 (through parameters) both PROVED
#     at HEAD and now FAIL CLOSED.
#   * COMPLETENESS is RECOVERED — 1123 (`1 / 3 == 0.3333333333333333`, TRUE in Python)
#     FAILED at HEAD and now PROVES. The old model was unsound one way and incomplete the
#     other; the new one is right both ways.
#   * NOTHING IS LOST — 0813, the WL-02 POSITIVE regression lock, keeps ALL FIVE clauses
#     (`5/2 == 2.5`, `1/2 == 0.5`, `7/2 == 3.5`, `4/2 == 2.0`, and the `//` int guard).
#     The projected cost of retiring them did not materialise, because folding preserves
#     exactly the cases where the exact-real answer was already right.
#   * 0814, the expected-FAIL negative lock, still FAILS (its claim is a real-vs-int TYPE
#     error, untouched by any value-level change).
#
# MEASURED L3: corpus 2 of 919 emissions move (0813, 0814 — and the diff is exactly the
# fold: `(float_truediv_op 5 2)` becomes `2.5`), mirrors 0 of 53, BYTE-INERT in all three
# directions. Ledger 3. Metric 456/481/25/0 unchanged.
#
# KEPT INLINE, NOT FACTORED INTO A HELPER, and that was a deliberate call: a new live
# method would be a live-only function the mirror does not model, moving the
# `check-mirror-coverage` ratchet. The first attempt DID add a helper and the plane went
# RED within minutes — the same trap the previous handoff recorded for `_dv_absent_opaque`.
# `_handle_binop` is `\trusted` in the mirror, so inline code there costs neither the
# ratchet nor the metric.
#
# WITNESSES: 1121 (FAIL), 1122 (FAIL), 1123 (PASS — was FAILING), 1124 (PASS, congruence).
#
# ===================== the original report follows, unchanged ====================
#
# OPEN ROUTE #58 — int/int TRUE DIVISION IS AN EXACT REAL DIVISION, SO IT DECIDES A
# COMPARISON PYTHON ANSWERS THE OTHER WAY
# (found 2026-09-10 by relaunch #51 generation #3, WHILE CLOSING ROUTE #53, by probing
#  #53's own repair for the gap it leaves)

## THE DEMONSTRATION (default `hoare` model, no flags, at the tree WITH route #53 landed)

`scratchpad/w51g3/r53/td3.py` — **`[+] Verification SUCCESS`**:

```python
#@ ensures \result > 0.3333333333333333     # <-- FALSE OF THE PROGRAM
#@ assigns \nothing
def f() -> float:
    return 1 / 3
```

Python:

```
>>> (1/3) > 0.3333333333333333
False
>>> repr(1/3)
'0.3333333333333333'
```

`1 / 3` and the literal `0.3333333333333333` are the **same binary64 value** — the literal
is precisely the shortest decimal that round-trips to it. So the strict `>` is False in
Python. Over the EXACT reals, one third is `0.333…` repeating and is genuinely greater than
the terminating 16-digit decimal, so the goal closes.

## WHY ROUTE #53'S REPAIR DOES NOT COVER IT

Route #53 made float-operand arithmetic go through one uninterpreted deterministic symbol.
That path is guarded by `if raw_op in _FARITH and _lf and _rf` — **both operands must be
float**. `1 / 3` has two INT operands and takes an entirely different branch, which bundles
the int→real lift and the division into its own bridge:

```
val float_truediv_op (a b: int) : real
    ensures { result = from_int a /. from_int b }
```

That `ensures` is the same defect as #53's, one costume over: it ties the bridge to Why3's
EXACT real division. The two routes are siblings and the second is invisible from the first,
because the code paths never meet.

**THIS IS THE GENERAL LESSON, AND IT IS THE SAME ONE ROUTES #50/#51 PAID FOR AT `str`:**
a repair covers the PATH it edits, not the SEMANTICS it means to fix. After closing a route,
probe the OTHER paths that reach the same semantics before recording it as closed.

## THE COST IS DIFFERENT FROM #53'S, AND THAT IS WHY THIS IS A SEPARATE ROUTE

`5 / 2 == 2.5` is TRUE of the program and PROVES today. It is exactly representable in
binary64, so it is one of the cases where the exact-real answer and the IEEE answer agree.
Making the bridge uninterpreted retires it — and `5 / 2 == 2.5` is the **headline example of
the WL-02 true-division fix on two normative surfaces**:

    docs/pycsl-concrete-syntax-reference.md:601
    docs/pycsl-translational-reference.md:235-236
    test-suite/annotations.md:800

So the repair is not a one-line copy of #53's: it costs a documented, advertised capability,
and those surfaces must be corrected honestly in the same increment rather than left saying
something the model no longer does.

## THE MODEL CANNOT TELL THE TWO CASES APART

The tempting narrow repair — keep the exact `ensures` when the quotient IS representable —
is not expressible here: representability is a property of the VALUE, and the bridge is
declared over all `a b: int` before any value is known. Constant-folding it for literal
operands would cover `5 / 2` and miss every non-literal, i.e. it would make the model's
honesty depend on whether the programmer wrote a constant. NOT MEASURED, NOT ATTEMPTED —
recorded here so the next window does not rediscover the idea and spend the window on it.


## THE EXACT SHAPE OF THE DEFECT, MEASURED IN BOTH DIRECTIONS

Probed at the tree with #53 landed (`scratchpad/w51g3/r53/td*.py`):

    td3  literal `1 / 3`, `\result > 0.3333333333333333`      PROVES   <-- FALSE in Python
    td4  PARAMETERS a==1, b==3, `\result > 0.333...3`          PROVES   <-- FALSE in Python
    td5  PARAMETERS a==2, b==3, `\result == 0.666...6`         FAILS    <-- TRUE in Python
    0813 literal `5 / 2 == 2.5` (and 1/2, 7/2, 4/2)             PROVES   <-- TRUE in Python

**td4 IS THE ONE THAT MATTERS.** The route is NOT literal constant-folding: it reaches
through PARAMETERS, so any contract that puts an ordering on a computed quotient — the
everyday `#@ ensures \result > 0.5` over `a / b` — is decided over the exact reals.

**td5 SHOWS THE MODEL IS ALREADY INCOMPLETE HERE**, which sharpens what the repair costs.
The exact-real quotient and the binary64 quotient agree EXACTLY when the quotient is
REPRESENTABLE. So today's lowering is:

    * SOUND and complete   when the quotient is representable  (0813's four cases)
    * UNSOUND              on orderings, where exact and binary64 straddle the literal (td3, td4)
    * already INCOMPLETE   on equalities with a non-representable quotient (td5)

The model cannot tell the three apart, because representability is a property of the VALUE
and the bridge is declared over all `a b: int` before any value is known.

## MEASURED BLAST RADIUS (emission diff, not source grep)

    corpus emissions containing `float_truediv_op`    2 — 0813 and 0814, and NOTHING else
    mirror emissions containing `float_truediv_op`    0 — BYTE-INERT

0814 is `# pycsl-expected: FAIL` and stays failing (its claim is a real-vs-int TYPE error,
which survives any value-level change). So the entire cost sits in 0813, the WL-02 POSITIVE
regression lock, whose four exact-value clauses a plain uninterpreted bridge would retire.
The WL-02 property itself stays locked NEGATIVELY by 0814.

## STATUS

CLOSED (see the header). The original status line as written when it was found:
OPEN. Reproduction above, live at the tree with #53 landed. Repair scoped (make the bridge
one uninterpreted deterministic symbol, exactly as #53 did) but its L3 corpus cost is
UNMEASURED — the `5 / 2` shape appears in the corpus and each occurrence must be found and
re-stated, which is the real work here.
