"""Test 0150 — PyCSL Annotation Reference 5.3 (variation A)"""
_ = 0  # anchor
#@ requires \length(arr) >= n
#@ requires n >= 0
#@ ensures \result == n
def test_store_clear(arr: list, n: int) -> int:
    """Store model: clear array, return count."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = 0
        i = i + 1
    return i

if __name__ == "__main__":
    a = [5, 6, 7]
    assert test_store_clear(a, 3) == 3
