"""Test 0078 — PyCSL Annotation Reference 2.4.1 (variation A)"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures arr[0] == \old(arr[0]) + 3
#@ assigns arr[0..1]
def test_label_multi_step(arr: list) -> None:
    """Multiple steps between label and check."""
    #@ label START
    arr[0] = arr[0] + 1
    arr[0] = arr[0] + 1
    arr[0] = arr[0] + 1

if __name__ == "__main__":
    a = [5]
    test_label_multi_step(a)
    assert a[0] == 8
