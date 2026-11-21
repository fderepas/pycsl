# ROUTE #53 — **CLOSED** 2026-09-10 by relaunch #51 (generation #3).
# A PYTHON `float` WAS MODELLED AS AN EXACT REAL, SO ROUNDING DID NOT EXIST.
# (found 2026-09-08 by relaunch #49 at `223424b9`; closed at `11eb06a0`+1)
#
# ## HOW IT WAS CLOSED, AND WHAT IT COST — ALL MEASURED, NONE ESTIMATED
#
# THE FIX, one site in `module6_whyml/expressions.py`: the float arithmetic bridge was
# `val float_add_op (a b: real) : real ensures { result = (a +. b) }` AND the SPEC path
# did not go through the bridge at all — it emitted `(left +. right)` outright. Both are
# now ONE UNINTERPRETED, DETERMINISTIC symbol used by the spec path and the body path
# alike: `val function float_{add,sub,mul,div}_op (a b: real) : real`.
#   * UNINTERPRETED is what stops any exact-real value, sign or ordering being decided.
#   * DETERMINISTIC is what keeps `\result == x + x` provable — body term and contract
#     term are the SAME term, so the goal closes by congruence. A non-deterministic `val`
#     with no `ensures` would also have closed the route, and would have made float
#     arithmetic say nothing at all. Witness 1120 is the control that pins this.
#
# NO SIGN CLAUSE WAS ADDED, and this is a decision, not an omission. `a >= 0.0 ->
# b >= 0.0 -> result >= 0.0` reads as IEEE-true, but its antecedent ranges over the Why3
# `real`, which cannot distinguish NaN — the identical shape was already measured to
# REFUTE for `*` (`0.0 * inf` is `nan`, not `0.0`). The honest repair for sign and bound
# facts is the error-carrying or `ieee_float.Float64` lowering recorded as candidates
# (1) and (3) below; it was not attempted here.
#
# ## MEASURED COST — AN ORDER OF MAGNITUDE BELOW THIS FILE'S OWN CENSUS
#
# The census below guessed "10 annotated files, both corpora" and warned the repair is
# "NOT byte-inert". The EMISSION DIFF (lesson (r): emission-diff before proof sweep) says:
#
#     pycsl-reference corpus     2 of 916 emissions move — 0517 and 0518, and NOTHING else
#     python-reference           0 move (0035, 0131 byte-identical; neither does float ARITHMETIC)
#     self-annotate mirrors      0 of 53 — BYTE-INERT in all three directions
#                                (0 MOVED, 0 GONE, 0 APPEARED)
#
# Because the mirror plane is byte-inert the repair owes **ZERO mirror re-proofs**, which
# is also why it could land while queue G was still proving route #57's seven movers.
#
# The whole cost is ONE clause in ONE corpus file: 0517's `ensures \result >= 0.0`, which
# is TRUE of the program and no longer proves. That is COMPLETENESS, not soundness, it is
# stated in 0517's own docstring rather than hidden, and 0518 (the `pycsl-expected: FAIL`
# negative twin) still fails as it must.
#
# ## A SECOND UNSOUND SHAPE THIS FILE DID NOT RECORD, FOUND WHILE CLOSING IT
#
# This file says the float ORDERING form "fails closed today". That was measured on the
# TRUE direction only: `\result > 0.3` (true of the program) indeed does not prove — a
# completeness gap. The FALSE direction went the other way: **`\result <= 0.3` PROVED**,
# and `0.1 + 0.2 <= 0.3` is False in Python. So the model was UNSOUND in the direction
# that asserts something false and INCOMPLETE in the direction that asserts something
# true — exactly the wrong way round, and probing only the fails-closed direction would
# have certified the ordering as safe. Witness 1119. **THE LESSON: when a route is
# recorded as "fails closed", check WHICH DIRECTION was measured.**
#
# ## WITNESSES (moved into the corpus in the closing increment, per the standing rule)
#
#     1117  `\result == 0.3` for `0.1 + 0.2`          FAIL (proved at HEAD)
#     1118  the same through a PARAMETER                FAIL (proved at HEAD)
#     1119  the ORDERING `\result <= 0.3`             FAIL (proved at HEAD)
#     1120  POSITIVE control `\result == x + x`       PASS before AND after
#
# ## WHAT THIS REPAIR DOES *NOT* CLOSE — ROUTE #58, FOUND BY PROBING ITS OWN GAP
#
# int/int TRUE DIVISION has its OWN bridge, `val float_truediv_op (a b: int) : real
# ensures { result = from_int a /. from_int b }`, on a DIFFERENT code path (both operands
# are ints, so the float-operand test above never fires). It still divides over the exact
# reals, and **`1 / 3 > 0.3333333333333333` PROVES** while Python answers False — the two
# are the SAME binary64 value. Recorded as route #58.
#
# ===================== the original report follows, unchanged ====================
#
# OPEN ROUTE #53 — A PYTHON `float` IS MODELLED AS AN EXACT REAL, SO ROUNDING DOES NOT EXIST
# (found 2026-09-08 by relaunch #49 at `223424b9`)

## The demonstration (`scratchpad/w49/probeinv/fl3.py`, `[+] Verification SUCCESS`)

```python
#@ ensures \result == 0.3          # <-- FALSE OF THE PROGRAM
#@ assigns \nothing
def f() -> float:
    return 0.1 + 0.2               # Python: 0.30000000000000004
```

and through a parameter as well (`fl4.py`, also `SUCCESS`):

```python
#@ requires x == 0.1
#@ ensures \result == 0.3
def f(x: float) -> float:
    return x + 0.2
```

`τ(float) = real` (docs/pycsl-static-semantics-reference.md:193). Why3's `real` is the
EXACT mathematical real, where `0.1 + 0.2 = 0.3` holds; Python's `float` is IEEE 754
binary64, where it does not. The model therefore proves an equality the program refutes.

**THIS IS THE DOCUMENTED MODEL, WHICH IS WHY IT MATTERS.** The static-semantics reference
introduces `τ(float) = real` as the FIX for "the unsound `τ(float) = int`", and the README
lists the model's float limitations as "mixed float-int & transcendentals out of scope".
Neither says that the model is exact where the language rounds. A limitation nobody wrote
down is one every reader assumes away.

## The ordering direction is affected too, and it is the sneakier one

`0.1 + 0.2 > 0.3` is TRUE in Python (`0.30000000000000004 > 0.3`) and FALSE over the reals.
Measured: the *guard* form fails closed today (`fl2.py`) because a float literal comparison
in a body guard is not modelled at all — a completeness gap that happens to hide half of this
route. The CONTRACT form is what decides, and that is what fl3/fl4 exercise.

## CENSUS (this tree)

    pycsl-reference files mentioning `float`            17
    files with a `: float` / `-> float` annotation      10 (both corpora)
    mirror files with a float annotation                 4
    src/pycsl_lib float mentions                        63

So a repair is NOT byte-inert and its cost must be measured against those.

## THREE CANDIDATE REPAIRS

1. **Model the real thing.** Why3 has `ieee_float.Float64`; the arithmetic operators become
   `fadd`/`fsub`/`fmul` with a rounding mode, and `0.1` is the binary64 literal nearest to
   one tenth. This is the only repair that makes float contracts MEAN what they say. Cost:
   every float lowering changes, SMT support for FP is uneven (Z3 has it, Alt-Ergo is
   partial), and the corpus's float drivers must be re-proved.
2. **Refuse the decidable float claim.** Keep `real`, but refuse an EQUALITY (and the
   orderings) in a contract when either side is a COMPUTED float — an arithmetic expression
   rather than a literal or a parameter. Fail-closed, cheap, and it states the truth: this
   model cannot decide such a claim. Cost: the ten annotated files, several of which exist
   precisely to state float postconditions.
3. **Carry the error.** Lower float arithmetic to `real` plus an explicit relative-error
   bound (`|r - (a+b)| <= eps * |a+b|`, `eps = 2^-53`), so `\result == 0.3` becomes
   unprovable while `|\result - 0.3| < 1e-9` still proves. The faithful middle, and the
   most work.

**RECOMMENDATION: (2) FIRST, as a fail-closed stop-gap that can land in one increment, with
(1) or (3) recorded as the real repair.** The campaign's rule is that a wrong answer is worse
than no answer, and today this model gives a wrong answer to the FIRST question anyone asks
about a float.
