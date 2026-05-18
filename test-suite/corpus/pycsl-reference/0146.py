"""Test 0146 — PyCSL Annotation Reference 5.1 (variation A)"""
_ = 0  # anchor
#@ requires \length(arr) >= 2
#@ ensures arr[0] == arr[1]
#@ assigns arr[0..1]
def test_hoare_copy(arr: list) -> None:
    """Hoare model: copy second element to first."""
    arr[0] = arr[1]

if __name__ == "__main__":
    a = [0, 7]
    test_hoare_copy(a)
    assert a[0] == 7
