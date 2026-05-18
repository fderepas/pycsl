"""Test 0089 — PyCSL Annotation Reference 3.1.6 (variation B)"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures arr[0] == \old(arr[0]) + 10
#@ assigns arr[0..1]
def test_old_add_ten(arr: list) -> None:
    """Old: adding a constant."""
    arr[0] = arr[0] + 10

if __name__ == "__main__":
    a = [3]
    test_old_add_ten(a)
    assert a[0] == 13
