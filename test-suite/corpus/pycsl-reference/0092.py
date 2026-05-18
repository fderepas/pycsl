"""Test 0092 — PyCSL Annotation Reference 3.1.8 (variation A)"""
_ = 0  # anchor
#@ requires \length(arr) >= 2
#@ ensures \result == \length(arr) - 1
def test_length_minus_one(arr: list) -> int:
    """ArrayLength used in arithmetic expression."""
    return len(arr) - 1

if __name__ == "__main__":
    assert test_length_minus_one([1, 2, 3]) == 2
