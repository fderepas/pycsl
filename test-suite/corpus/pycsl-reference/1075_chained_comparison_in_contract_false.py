"""Test 1075 — the companion NEGATIVE for 1074: a chain that is FALSE of the body must
still fail.

FALSE OF THE PROGRAM: `f()` returns 500, which is not in `0 <= \\result <= 10`.

1074 shows the chain now MEANS the conjunction; this file shows it does not mean `true`.
An expansion that dropped the tail (the route #33 defect, in clause position) would leave
`0 <= \\result`, which 500 satisfies, and this file would pass. An expansion that collapsed
to a constant would do the same. So the capability and this refutation are two halves of
one measurement.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures 0 <= \result <= 10
#@ assigns \nothing
def f() -> int:
    return 500
