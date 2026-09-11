"""1159 — ROUTE #66 POSITIVE CONTROL: a VALID `chr` still discharges.

The bound is exact, so this is a real obligation and not a ban on `chr`. Without this
control, refusing every `chr` under a `no_exception` context would satisfy 1158.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    return len(chr(65))
