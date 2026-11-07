"""Test 1049 — ROUTE #40 positive control: `... is Ellipsis` is TRUE, and proving it
is a capability rather than the accident it used to be.

Before route #40 this proved because BOTH sides were the literal `0`. After the literal
half was made opaque and before 1048's fix it stopped proving. Now both spellings lower
to the SAME opaque constant, so `pycsl_ellipsis = pycsl_ellipsis` discharges — for the
right reason.

If this ever starts failing, the two spellings of the singleton have drifted apart
again.
"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = ...
    if x is Ellipsis:
        return 0
    return 1
