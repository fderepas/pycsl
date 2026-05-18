"""Test 0122 — PyCSL Annotation Reference 3.4.3 (variation A)"""
_ = 0  # anchor
#@ requires \length(arr) >= 3
#@ ensures arr[0] == 1
#@ ensures arr[1] == 2
#@ ensures arr[2] == 3
#@ assigns arr[0..3]
def test_assigns_three(arr: list) -> None:
    """Assigns: three elements."""
    arr[0] = 1
    arr[1] = 2
    arr[2] = 3

if __name__ == "__main__":
    a = [0, 0, 0]
    test_assigns_three(a)
    assert a == [1, 2, 3]
