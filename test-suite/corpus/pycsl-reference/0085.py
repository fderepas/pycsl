"""Test 0085 — PyCSL Annotation Reference 3.1.4 (variation B)"""
_ = 0  # anchor
#@ requires \length(arr) > i
#@ requires \length(arr) > j
#@ requires i >= 0
#@ requires j >= 0
#@ ensures \result == arr[i] + arr[j]
def test_subscript_two_indices(arr: list, i: int, j: int) -> int:
    """Subscript with two index variables."""
    return arr[i] + arr[j]

if __name__ == "__main__":
    assert test_subscript_two_indices([10, 20, 30], 0, 2) == 40
