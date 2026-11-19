r"""Test 1407 — ROUTE #138: gen #26 draft-9 keyed the module-scope SUBSCRIPT store on the path, and a mutating METHOD CALL is the same sink one spelling over. `f.__globals__.__setitem__("N", 5)` at module scope PROVED `f() == 3` while CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


f.__globals__.__setitem__("N", 5)