"""Test 0121 — PyCSL Annotation Reference 3.4.2 (variation B)"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures arr[0] == \old(arr[0]) + 5
#@ assigns arr[0..1]
def test_assigns_add(arr: list) -> None:
    """Assigns: modify by adding 5."""
    arr[0] = arr[0] + 5

if __name__ == "__main__":
    a = [10]
    test_assigns_add(a)
    assert a[0] == 15
