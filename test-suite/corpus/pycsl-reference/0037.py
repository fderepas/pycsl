"""Test 0037 — PyCSL Annotation Reference 4.3"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures \result == arr[0]
def test_no_len(arr: list) -> int:
    """len() is NOT supported in contracts — use \length(arr)."""
    return arr[0]

if __name__ == "__main__":
    assert test_no_len([99]) == 99
