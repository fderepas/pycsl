"""Test 1042 — ROUTE #41 negative witness (b): a non-empty SET literal compared to 0.

FALSE OF THE PROGRAM: `{1,2,3} == 0` is False, so Python returns 0.
At the parent commit c37f0059 `\result == 7` PROVED. See 1041.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = {1, 2, 3}
    if x == 0:
        return 7
    return 0
