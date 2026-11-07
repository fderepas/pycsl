"""Test 1027 — ROUTE #36, the SEQUENCE half: the loop variable of a `for x in
<array param>` loop did not survive the loop either.

FALSE OF THE PROGRAM: after the loop `x` is the LAST element, 7, so Python
returns 7.

The index half (1025/1026) was closed first because `elem_expr` IS the counter
there and is int-typed like the outer ref. The general element write-back is NOT
well-typed — the outer ref takes its type from the FIRST assignment to that name,
which need not be the loop's element type, and an unconditional version measured
mirror L3-tc 51/53. This case is admitted on a pair of conditions that pin BOTH
types: the target is in none of the non-int local classes (so its outer ref is
the integer `ref 0` pre-declaration), and the iterable is a formal parameter
whose symbol type is `list` (so its element is an `int`).

`_current_array1d_params` is NOT the right source for that second half — it is
EMPTY at the binder for a plain `a: list` parameter, and the first version of
this widening therefore never fired at all while looking exactly like it had.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires \length(a) == 2
#@ requires a[0] == 1
#@ requires a[1] == 7
#@ ensures \result == 0
#@ assigns \nothing
def f(a: list) -> int:
    x = 0
    for x in a:
        pass
    return x
