r"""Test 1984 — gen #36 (expected FAIL): ROUTE #232 — a keyword-only parameter behind a modelled `*args`

`def f(*vals: str, k: int)` would need the vararg packing to stop before `k`; that is not built,
so the shape is refused fail-closed rather than letting the packing absorb (or the signature
drop) the keyword-only parameter. CPython: `g()` returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == k
#@ assigns \nothing
def f(*vals: str, k: int) -> int:
    return k


#@ ensures \result == 5
#@ assigns \nothing
def g() -> int:
    return f("a", "b", k=5)
