"""Test 0046 — PyCSL Annotation Reference 5.3"""
_ = 0  # anchor
#@ requires \length(arr) >= n
#@ requires n >= 0
#@ ensures \result == n
def test_store_model(arr: list, n: int) -> int:
    """Store model: single untyped heap."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = i
        i = i + 1
    return i

if __name__ == "__main__":
    a = [0, 0, 0]
    assert test_store_model(a, 3) == 3
    assert a == [0, 1, 2]
