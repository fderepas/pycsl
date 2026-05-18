"""Test 0007 — PyCSL Annotation Reference 2.4.1"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures arr[0] == \old(arr[0]) + 1
#@ assigns arr[0..1]
def test_label(arr: list) -> int:
    """Label marks a program point for \at references."""
    #@ label PRE
    arr[0] = arr[0] + 1
    return arr[0]

if __name__ == "__main__":
    a = [10]
    assert test_label(a) == 11
