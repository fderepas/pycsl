"""1164 — ROUTE #68 POSITIVE CONTROL: valid `**` and `<<` still discharge.

Both bounds are exact, so these are real obligations rather than a ban on the operators.
Without this control, refusing every power/shift under a `no_exception` context would
satisfy 1162 and 1163.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    return (2 ** 3) + (1 << 3)
