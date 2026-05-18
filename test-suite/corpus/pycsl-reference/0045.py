"""Test 0045 — PyCSL Annotation Reference 5.2"""
_ = 0  # anchor
#@ requires \length(arr) >= n
#@ requires n >= 0
#@ ensures \result == n
def test_typed_model(arr: list, n: int) -> int:
    """Typed model: heap-based arrays with map loc int."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = i
        i = i + 1
    return i

if __name__ == "__main__":
    a = [0, 0, 0]
    assert test_typed_model(a, 3) == 3
    assert a == [0, 1, 2]
