"""Test 1246 — ROUTE #90 CERTIFIED BOUNDARY: the comparison arm is ADMITTED then ILL-TYPED.

TRUE OF THE PROGRAM: with `a > b`, `(a > b) is True` is True in CPython, so f(3, 1) = 7.
MEASURED. The claim below is therefore TRUE, and PyCSL still does not prove it.

THIS IS NOT A ROUTE AND NOT A REGRESSION — IT IS A PRE-EXISTING COMPLETENESS GAP, MEASURED
AT BOTH TREES. Route #42's whitelist admits a comparison BinOp as an operand (`a
comparison yields a bool`), so the guard does NOT refuse this file; the emission is then
`if ((a > b) = 1)`, which compares a Why3 `bool` to the `int` 1 and is rejected by Why3's
typechecker: `This expression has type bool, but is expected to have type int`. Verified
in a detached worktree at the PRE-REPAIR HEAD — identical failure, identical message — so
route #90's deletion of the annotation arm did not cause it.

WHY IT IS WORTH A FILE. Route #42's whitelist looked like a four-arm capability. Measured,
it was one TAUTOLOGY (`True is True`, see 1245) plus one UNSOUND arm (the annotation arm,
routes #90's carriers 1240-1244), with the two arms that were supposed to carry the real
capability — a comparison result and `not X` — ADMITTED BUT DEAD. **AN ARM THAT IS
WHITELISTED AND THEN FAILS TO TYPECHECK LOOKS EXACTLY LIKE A WORKING ARM IN THE WHITELIST
AND EXACTLY LIKE A REFUSAL AT THE COMMAND LINE.** Nobody had ever run it.

REOPENING CONDITION: if the bool-as-int convention is ever extended so a comparison
lowers to an `int`-valued expression, this file must start PASSING, and it should then be
re-marked as a positive control. Until then it is a fail-closed boundary.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires a > b
#@ ensures \result == 7
#@ assigns \nothing
def f(a: int, b: int) -> int:
    if (a > b) is True:
        return 7
    return 0
