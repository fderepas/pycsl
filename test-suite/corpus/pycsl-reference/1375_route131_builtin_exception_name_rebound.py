r"""Test 1375 — ROUTE #131 (exception arm, order 2): `ValueError = KeyError` at module scope; `raise ValueError("x")` was lowered as the builtin `ValueError`, not caught by `except KeyError`, so the escaping exception made the false `\result == 1` PROVE while CPython catches it and returns 2. The first repair draft keyed on CALLS of a short builtin list; any read of a rebound builtin name is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
ValueError = KeyError


#@ ensures \result == 1
#@ assigns \nothing
def f(x: int) -> int:
    y = x
    y = y + 1
    try:
        raise ValueError("x")
    except KeyError:
        return 2
    return 1
