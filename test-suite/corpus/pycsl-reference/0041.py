"""Test 0041 — PyCSL Annotation Reference 4.7"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures \result == arr[0]
def test_no_in_operator(arr: list) -> int:
    """in / not in are NOT supported in contracts."""
    return arr[0]

if __name__ == "__main__":
    assert test_no_in_operator([42]) == 42
