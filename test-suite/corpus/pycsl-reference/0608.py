"""Test 0608 — negative: a false fact about a tuple-array element is unprovable (07-0903 W1).

Same `array (int, int)` model as 0607, but the postcondition over-claims `\result == 11` while
`a[0][0]` is `10`. The concrete element destructure makes the VC refute it — confirming the
tuple array is modelled precisely (each component recovered), not collapsed to an opaque int.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 11
#@ assigns \nothing
def first_first() -> int:
    a = [(10, 20), (30, 40)]
    return a[0][0]
