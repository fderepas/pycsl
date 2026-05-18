"""Test 0011 — PyCSL Annotation Reference 3.1.4"""
_ = 0  # anchor
#@ requires \length(arr) > i
#@ requires i >= 0
#@ ensures \result == arr[i]
def test_subscript_access(arr: list, i: int) -> int:
    """SubscriptAccess atom: arr[i] in contracts."""
    return arr[i]

if __name__ == "__main__":
    assert test_subscript_access([10, 20, 30], 1) == 20
