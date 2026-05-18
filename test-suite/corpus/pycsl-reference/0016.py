"""Test 0016 — PyCSL Annotation Reference 3.1.9"""
_ = 0  # anchor
#@ requires \valid(arr, n)
#@ requires n >= 1
#@ ensures \result == arr[0]
def test_valid(arr: list, n: int) -> int:
    """Valid atom: \valid(arr, n) asserts arr[0..n) is allocated."""
    return arr[0]

if __name__ == "__main__":
    assert test_valid([5, 6, 7], 3) == 5
