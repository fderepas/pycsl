r"""Test 1911 — gen #32 (expected FAIL): ROUTE #227's LITERAL arm, negative-tested.

`None + 5` raises `TypeError`. This arm of the fence had a census population of ZERO across
4531 files, and a guard whose population is empty has checked nothing while looking exactly
like a guard that passed — so it gets its own witness, written by REMOVING the thing the
guard should catch from every other file and putting it here alone.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 5
#@ no_exception \all
#@ assigns \nothing
def f() -> int:
    return None + 5
