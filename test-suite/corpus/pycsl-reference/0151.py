"""Test 0151 — PyCSL Annotation Reference 5.3 (variation B)"""
_ = 0  # anchor
#@ requires \length(arr) >= n
#@ requires n >= 1
#@ ensures \result == n + n
def test_store_sum(arr: list, n: int) -> int:
    """Store model: write to array, return n+n."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = i + 1
        i = i + 1
    return n + n

if __name__ == "__main__":
    a = [0, 0]
    assert test_store_sum(a, 2) == 4
