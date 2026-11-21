"""1150 — ROUTE #64 POSITIVE CONTROL: an IN-RANGE byte store still discharges.

The repair adds a real proof obligation, it does not blanket-refuse bytes stores. A store
of a value that IS in [0, 256) must still prove under the strongest `no_exception` claim —
otherwise the fix is a refusal wearing a trigger's clothes, and 1149 would pass for the
wrong reason.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures \result == 9
#@ assigns \nothing
def f() -> int:
    b = bytearray([1])
    b[0] = 9
    return b[0]
