r"""Test 1983 — gen #36 (expected PASS): ROUTE #232 — positional-only and ordinary parameters together

`f(a, /, b)` called `f(1, b=2)`: `a` binds by position, `b` by name. Before the repair `a` was
dropped and the contract naming it was refused. CPython: `g()` returns -1.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == a - b
#@ assigns \nothing
def f(a: int, /, b: int) -> int:
    return a - b


#@ ensures \result == -1
#@ assigns \nothing
def g() -> int:
    return f(1, b=2)
