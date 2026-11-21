"""Test 1061 — ROUTE #44 negative witness (d): a CONTRACT `\\result == None` PROVED.

FALSE OF THE PROGRAM: `f()` returns the int `0`, and `0 == None` is False in Python.

This is the worst of route #44's four, and the one that needs no branch at all: the
contract itself is false of its program and proves DIRECTLY, because `\\result == None`
lowered to `result = 0` and the function returns 0. Nothing about the body is unusual —
any function returning 0 could carry this contract and be "verified". At the parent
commit d0493cea it PROVED.

Its positive twin is `pycsl-reference/0229` (`ensures \\result != None`), which had been
proving only BY ACCIDENT as `result <> 0`; it now lowers to the semantically exact
`true`, because an `int`-returning function is never the `None` singleton.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == None
#@ assigns \nothing
def f() -> int:
    return 0
