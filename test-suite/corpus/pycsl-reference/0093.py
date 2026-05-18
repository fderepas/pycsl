"""Test 0093 — PyCSL Annotation Reference 3.1.8 (variation B)"""
_ = 0  # anchor
#@ requires \length(arr) > 0
#@ ensures \result >= 1
def test_length_positive(arr: list) -> int:
    """ArrayLength in ensures: non-empty array."""
    return len(arr)

if __name__ == "__main__":
    assert test_length_positive([42]) == 1
