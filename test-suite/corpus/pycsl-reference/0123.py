"""Test 0123 — PyCSL Annotation Reference 3.4.3 (variation B)"""
_ = 0  # anchor
#@ requires \length(arr) >= 2
#@ ensures arr[0] == \old(arr[1])
#@ ensures arr[1] == \old(arr[0])
#@ assigns arr[0..2]
def test_assigns_swap(arr: list) -> None:
    """Assigns: swap two elements."""
    tmp = arr[0]
    arr[0] = arr[1]
    arr[1] = tmp

if __name__ == "__main__":
    a = [1, 2]
    test_assigns_swap(a)
    assert a == [2, 1]
