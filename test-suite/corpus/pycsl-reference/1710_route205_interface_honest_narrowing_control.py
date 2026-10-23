r"""Test 1710 — ROUTE #205 CONTROL: an HONEST interface narrowing must keep proving.

Identical in shape to 1709 except the interface claims something the definition really
establishes (`\result >= 0` from `\result == 3`). Route #205's fix emits the narrowing
goal in every unit that shows the `val`, so this file — and every importer of it — must
still verify. If this ever fails, the fix has become a ban on `#@ interface`.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ assigns \nothing
#@ ensures \result == 3
#@ interface ensures \result >= 0
def three_ok() -> int:
    return 3
