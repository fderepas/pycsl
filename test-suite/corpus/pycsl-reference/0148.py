"""Test 0148 — PyCSL Annotation Reference 5.2 (variation A)"""
_ = 0  # anchor
#@ requires \length(arr) >= n
#@ requires n >= 0
#@ ensures \result == n + 1
def test_typed_fill(arr: list, n: int) -> int:
    """Typed model: fill array and return count+1."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = 0
        i = i + 1
    return i + 1

if __name__ == "__main__":
    a = [1, 1]
    assert test_typed_fill(a, 2) == 3
