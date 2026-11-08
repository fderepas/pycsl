r"""Test 1976 — gen #36 (expected PASS): ROUTE #232 — positional + keyword-only, default omitted and given

`f(a, b, *, k, m=2)`: positional actuals bind `a`, `b`; `k` binds by name; an omitted `m`
takes its literal default 2 and a given one its actual. CPython: `g()` returns 123 + 120 = 243.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == a * 100 + b * 10 + k - m
#@ assigns \nothing
def f(a: int, b: int, *, k: int, m: int = 2) -> int:
    return a * 100 + b * 10 + k - m


#@ ensures \result == 243
#@ assigns \nothing
def g() -> int:
    return f(1, 2, k=5) + f(1, 2, m=5, k=5)
