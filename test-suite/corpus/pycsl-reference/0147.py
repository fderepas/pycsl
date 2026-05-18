"""Test 0147 — PyCSL Annotation Reference 5.1 (variation B)"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures \result == arr[0]
def test_hoare_read(arr: list) -> int:
    """Hoare model: read from array."""
    return arr[0]

if __name__ == "__main__":
    assert test_hoare_read([42]) == 42
