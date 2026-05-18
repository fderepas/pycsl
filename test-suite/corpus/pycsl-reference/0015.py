"""Test 0015 — PyCSL Annotation Reference 3.1.8"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures \result == \length(arr)
def test_array_length(arr: list) -> int:
    """ArrayLength atom: \length(arr) is the length of array arr."""
    return len(arr)

if __name__ == "__main__":
    assert test_array_length([1, 2, 3]) == 3
