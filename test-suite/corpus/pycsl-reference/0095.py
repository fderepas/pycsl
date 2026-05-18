"""Test 0095 — PyCSL Annotation Reference 3.1.9 (variation B)"""
_ = 0  # anchor
#@ requires \valid(arr, 1)
#@ ensures \result == arr[0] * 2
def test_valid_single(arr: list) -> int:
    """Valid with constant size."""
    return arr[0] + arr[0]

if __name__ == "__main__":
    assert test_valid_single([4]) == 8
