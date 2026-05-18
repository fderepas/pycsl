"""Test 0070 — PyCSL Annotation Reference 2.1.3 (variation A)"""
_ = 0  # anchor
#@ requires \length(arr) >= 2
#@ ensures arr[0] == 0
#@ ensures arr[1] == 1
#@ assigns arr[0..2]
def test_frame_two_elems(arr: list) -> None:
    """Frame condition assigning two elements."""
    arr[0] = 0
    arr[1] = 1

if __name__ == "__main__":
    a = [9, 9, 9]
    test_frame_two_elems(a)
    assert a[0] == 0 and a[1] == 1
