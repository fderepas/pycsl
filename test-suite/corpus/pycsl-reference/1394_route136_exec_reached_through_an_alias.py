r"""Test 1394 — ROUTE #136: the `exec` twin of test 1393 — `ex = exec; ex("N" + " = 5")` names none of the guarded spellings and PROVED `f() == 3` while CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3
ex = exec
ex("N" + " = 5")


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
