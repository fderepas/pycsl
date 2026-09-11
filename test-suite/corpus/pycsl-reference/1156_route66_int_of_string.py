"""1156 — ROUTE #66 NEGATIVE: `int(<str>)` under `no_exception ValueError`.

CPython raises `ValueError: invalid literal for int()`. There was no trigger row, and the
call lowers to an OPAQUE `val str_to_int (s: string) : int`, so no faithful obligation can
be injected — refused rather than discharged. Proved before the refusal.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception ValueError
#@ ensures True
#@ assigns \nothing
def f() -> int:
    return int("abc")
