"""1165 — ROUTE #68 NEGATIVE: `float(<str>)` under `no_exception ValueError`.

CPython raises `ValueError: could not convert string to float`. The emitted call is
`py_float_1 1824800645` — the STRING IS HASHED TO AN INT before reaching the opaque val, so
the argument is not merely unmodelled, it is gone and no condition over it can be written.
Refused rather than discharged. `float()` of a NUMBER is untouched and still proves.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception ValueError
#@ ensures True
#@ assigns \nothing
def f() -> int:
    x = float("abc")
    return 0
