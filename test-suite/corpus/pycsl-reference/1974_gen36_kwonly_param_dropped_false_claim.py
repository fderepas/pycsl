r"""Test 1974 — gen #36 (expected FAIL): ROUTE #232 — a keyword-only parameter dropped from the signature

`def f(*, k: int)` was emitted as `let function f () : int` with the body's read of `k` an
auto-declared opaque `val constant k : int`; both call sites became `f ()`, so
`f(k=3) == f(k=4)` PROVED at 3e758c0b. CPython: `g()` returns 0, so `\result == 1` is false.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ assigns \nothing
def f(*, k: int) -> int:
    return k


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if f(k=3) == f(k=4):
        return 1
    return 0
