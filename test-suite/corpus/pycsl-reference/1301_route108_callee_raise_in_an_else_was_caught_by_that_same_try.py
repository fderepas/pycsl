"""Test 1301 — ROUTE #108 negative witness: a callee's raise inside a try's `else:` was
CAUGHT by that same try, and was ALSO dropped from the enclosing function's `raises`
summary.

PYTHON'S RULE: in `try: B except E: H else: O`, an exception raised in `O` is NOT caught by
this try's own handlers. It propagates out of the function.

FALSE OF THE PROGRAM: `caller(-1)` RAISES ValueError, so the `#@ no_exception ValueError`
commitment is false. At the parent commit this PROVED (rc=0, Valid, 27 steps).

#108 IS THE OPPOSITE DIRECTION OF #107's ONE LINE. #107 is the block being DELETED; #108 is
the block being SPLICED WHERE PYTHON DOES NOT PUT IT. Appending the lowered `else` to the
try BODY puts it inside the try, where the handler arm catches it. A raise arriving through
a callee's `#@ raises` leaves NO literal `raise` in the lowered text, so the substring guard
PERMITTED the unsound splice. And `_callee_raised_in` recursed into a Try's `body` and
`handlers` and then `continue`d — never visiting `orelse` — so the summary dropped it too.

THE TWO DIRECTIONS HAD TO BE REPAIRED TOGETHER: making the splice fire more often is not
safe on its own, and fixing only the summary would leave the local catch wrong.

The callee is named `boom` on purpose, so that its NAME contributes no `raise` substring and
route #107's deletion cannot be what fires. The first attempt at this witness named it
`may_raise` and PROVED VIA #107's MECHANISM — caught only by reading the whole emitted file.

The positive twin is 1302.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ raises ValueError when x0 < 0
#@ ensures \result >= 0
def boom(x0: int) -> int:
    if x0 < 0:
        raise ValueError("neg")
    return x0

#@ assigns \nothing
def wrapper(k: int) -> int:
    y = 0
    try:
        y = 1
    except ValueError:
        y = 9
    else:
        boom(k)
    return y

#@ no_exception ValueError
def caller(k: int) -> int:
    return wrapper(k)
