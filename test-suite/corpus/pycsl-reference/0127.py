"""Test 0127 — PyCSL Annotation Reference 3.4.5 (variation B)"""
_ = 0  # anchor
#@ requires \length(arr) >= n
#@ requires n >= 0
#@ ensures \forall i; 0 <= i and i < n ==> arr[i] == 1
#@ assigns arr[0..n]
def test_region_fill_ones(arr: list, n: int) -> None:
    """Array region: fill with ones."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \forall j; 0 <= j and j < i ==> arr[j] == 1
    #@ loop variant n - i
    while i < n:
        arr[i] = 1
        i = i + 1

if __name__ == "__main__":
    a = [0, 0, 0]
    test_region_fill_ones(a, 3)
    assert a == [1, 1, 1]
