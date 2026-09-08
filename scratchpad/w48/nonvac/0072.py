"""Test 0072 — Python Reference 3.2.13.4: Slice objects"""
_ = 0  # anchor
#@ requires \length(a) == 5
#@ ensures \result == 0
#@ assigns \nothing
def test_slice_objects(a: list) -> int:
    """Ref 3.2.13.4: a slice object represents a RANGE — `a[i:j]` yields the elements from
    index `i` up to but NOT including `j`, so its length is `j - i` when both bounds are in
    range. The half-open convention is the section's content and it is what a lowering that
    used `j - i + 1`, or that clamped the wrong end, would get wrong. The contract pins the
    resulting length, which is a real obligation on the slice lowering rather than on any
    literal. Previously the whole body was `return 0` and the postcondition was discharged
    by the tail `return` alone (relaunch #46, `bin/check-vacuous-drivers.py`)."""
    b = a[1:4]
    if len(b) == 4:
        return 0
    return 1

if __name__ == "__main__":
    assert test_slice_objects([0, 1, 2, 3, 4]) == 0
