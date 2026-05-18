"""Test 0044 — PyCSL Annotation Reference 5.1"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures arr[0] == 0
#@ assigns arr[0..1]
def test_hoare_model(arr: list) -> None:
    """Hoare model (default): arrays are value-typed, no aliasing."""
    arr[0] = 0

if __name__ == "__main__":
    a = [5]
    test_hoare_model(a)
    assert a[0] == 0
