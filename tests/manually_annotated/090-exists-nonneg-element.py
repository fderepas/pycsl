"""Quantifier test: \exists — prove there is a non-negative element after
setting the first element to zero."""

#@ requires \valid(arr, n) and n >= 1
#@ assigns arr[0..n]
#@ ensures \exists i; 0 <= i and i < n and arr[i] >= 0
def ensure_nonneg(arr: list, n: int) -> int:
    arr[0] = 0
    return 0
