"""Test 0126 — PyCSL Annotation Reference 3.4.5 (variation A)"""
_ = 0  # anchor
#@ requires \length(arr) >= 3
#@ ensures arr[0] == 0
#@ ensures arr[1] == 0
#@ ensures arr[2] == 0
#@ assigns arr[0..3]
def test_region_clear(arr: list) -> None:
    """Array region assign: clear first 3 elements."""
    arr[0] = 0
    arr[1] = 0
    arr[2] = 0

if __name__ == "__main__":
    a = [1, 2, 3, 4]
    test_region_clear(a)
    assert a[:3] == [0, 0, 0]
