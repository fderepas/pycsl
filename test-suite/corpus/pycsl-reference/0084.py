"""Test 0084 — PyCSL Annotation Reference 3.1.4 (variation A)"""
_ = 0  # anchor
#@ requires \length(arr) >= 3
#@ ensures \result == arr[0] + arr[1] + arr[2]
def test_subscript_sum(arr: list) -> int:
    """Multiple subscript accesses in one contract."""
    return arr[0] + arr[1] + arr[2]

if __name__ == "__main__":
    assert test_subscript_sum([1, 2, 3]) == 6
