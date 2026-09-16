r"""Test 1411 — ROUTE #138: the same with a NON-CONSTANT text. `S = "f.__globals__.__setitem__(\x27N\x27, 5)"` with a bare in-function `eval(S)` PROVED `f() == 3` while CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3
S = "f.__globals__.__setitem__('N', 5)"


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


def g() -> None:
    eval(S)


g()