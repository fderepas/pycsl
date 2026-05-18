"""Test 0088 — PyCSL Annotation Reference 3.1.6 (variation A)"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures arr[0] == \old(arr[0]) * 2
#@ assigns arr[0..1]
def test_old_double(arr: list) -> None:
    """Old: doubling an element."""
    arr[0] = arr[0] + arr[0]

if __name__ == "__main__":
    a = [5]
    test_old_double(a)
    assert a[0] == 10
