"""Test 0034 — PyCSL Annotation Reference 3.4.5"""
_ = 0  # anchor
#@ requires \length(arr) >= n
#@ requires n >= 0
#@ assigns arr[0..n]
def test_assigns_array_region(arr: list, n: int) -> None:
    """Assigns arr[lo..hi]: array region may be mutated."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = 0
        i = i + 1

if __name__ == "__main__":
    a = [1, 2, 3]
    test_assigns_array_region(a, 3)
    assert a == [0, 0, 0]
