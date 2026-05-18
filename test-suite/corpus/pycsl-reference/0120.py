"""Test 0120 — PyCSL Annotation Reference 3.4.2 (variation A)"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures arr[0] == 0
#@ assigns arr[0..1]
def test_assigns_elem(arr: list) -> None:
    """Assigns single array element."""
    arr[0] = 0

if __name__ == "__main__":
    a = [99]
    test_assigns_elem(a)
    assert a[0] == 0
