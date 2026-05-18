"""Test 0094 — PyCSL Annotation Reference 3.1.9 (variation A)"""
_ = 0  # anchor
#@ requires \valid(arr, n)
#@ requires n >= 2
#@ ensures \result == arr[0] + arr[1]
def test_valid_two(arr: list, n: int) -> int:
    """Valid: access two elements from valid region."""
    return arr[0] + arr[1]

if __name__ == "__main__":
    assert test_valid_two([3, 7, 11], 3) == 10
