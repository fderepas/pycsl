"""Test 1022 — ROUTE #34 POSITIVE witness: the true twin of 1017.

`a[0]` is 9 after the store, and that is now PROVABLE — the fix removes a wrong
answer without removing the right one. The read falls through to the real array,
which the emission has always modelled faithfully.
"""
_ = 0  # anchor
#@ ensures \result == 9
#@ assigns \nothing
def f() -> int:
    a = [5]
    a[0] = 9
    return a[0]
