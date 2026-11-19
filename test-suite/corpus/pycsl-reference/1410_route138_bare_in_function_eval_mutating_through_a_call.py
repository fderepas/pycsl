r"""Test 1410 — ROUTE #138: the eval location gate is about where an ASSIGNMENT lands (a discarded locals snapshot inside a function); a mutation through a CALL does not care. A bare in-function `eval("f.__globals__.__setitem__(\x27N\x27, 5)")` PROVED `f() == 3` while CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


def g() -> None:
    eval("f.__globals__.__setitem__('N', 5)")


g()