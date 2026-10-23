r"""Test 1313 — ROUTE #115 negative: `(lambda y: y + 1)(x)` is an UnknownPyExpr in Module 5 and lowered to the LITERAL 0, so `\result == 0` PROVED (CPython x + 1). It is now `(any int)`.
"""
# pycsl-expected: FAIL
#@ requires x >= 0
#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    return (lambda y: y + 1)(x)
