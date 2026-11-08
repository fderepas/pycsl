r"""Test 1982 — gen #36 (expected FAIL): ROUTE #232 — a positional actual cannot reach a keyword-only formal

With `k` now an ordinary emitted parameter, `f(3)` must NOT bind it positionally: CPython raises
TypeError ("takes 0 positional arguments but 1 was given"). The call is refused fail-closed.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == k
#@ assigns \nothing
def f(*, k: int) -> int:
    return k


#@ ensures \result == 3
#@ no_exception \all
#@ assigns \nothing
def g() -> int:
    return f(3)
