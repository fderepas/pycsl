"""1174 — ROUTE #72 POSITIVE CONTROL: a NON-EMPTY literal separator still discharges.

The refusal is conservative — it allows only a non-empty string LITERAL — so the common
`s.split(" ")` must keep working under `no_exception \all`. Without this control the fix
would be a blanket ban on `split` and 1173 would pass for the wrong reason.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    s = "ab"
    parts = s.split(" ")
    return 0
