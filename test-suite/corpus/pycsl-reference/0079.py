"""Test 0079 — PyCSL Annotation Reference 2.4.1 (variation B)"""
_ = 0  # anchor
#@ requires \length(arr) >= 2
#@ ensures arr[0] == \old(arr[0]) + 1
#@ ensures arr[1] == \old(arr[1]) + 1
#@ assigns arr[0..2]
def test_label_two_arrays(arr: list) -> None:
    """Label with two array elements modified."""
    #@ label BEFORE
    arr[0] = arr[0] + 1
    arr[1] = arr[1] + 1

if __name__ == "__main__":
    a = [10, 20]
    test_label_two_arrays(a)
    assert a == [11, 21]
