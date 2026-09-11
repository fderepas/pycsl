"""1162 — ROUTE #68 NEGATIVE: `0 ** -1` under `no_exception \all`.

CPython raises `ZeroDivisionError: 0.0 cannot be raised to a negative power`. `**` lowers to
an opaque `py_pow` and had no trigger row. Both operands are available, so the condition
`not (base = 0 /\ exp < 0)` is exact.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    return 0 ** (-1)
