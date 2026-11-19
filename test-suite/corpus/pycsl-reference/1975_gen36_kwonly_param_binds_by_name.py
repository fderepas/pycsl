r"""Test 1975 — gen #36 (expected PASS): ROUTE #232 — a keyword-only actual binds its parameter

The faithful twin of 1974: `k` is an ordinary parameter of `f` (so its contract may name it)
and the call `f(k=3)` passes 3. CPython: `g()` returns 3.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == k
#@ assigns \nothing
def f(*, k: int) -> int:
    return k


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return f(k=3)
