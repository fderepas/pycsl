"""Test 0149 — PyCSL Annotation Reference 5.2 (variation B)"""
_ = 0  # anchor
#@ requires \length(arr) >= n
#@ requires n >= 1
#@ ensures \result == n * 2
def test_typed_double(arr: list, n: int) -> int:
    """Typed model: write and return doubled count."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = i + i
        i = i + 1
    return n * 2

if __name__ == "__main__":
    a = [0, 0, 0]
    assert test_typed_double(a, 3) == 6
