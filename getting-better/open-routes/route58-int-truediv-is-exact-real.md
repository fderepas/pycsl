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

## STATUS

OPEN. Reproduction above, live at the tree with #53 landed. Repair scoped (make the bridge
one uninterpreted deterministic symbol, exactly as #53 did) but its L3 corpus cost is
UNMEASURED — the `5 / 2` shape appears in the corpus and each occurrence must be found and
re-stated, which is the real work here.
