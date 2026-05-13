"""Quantifier test: \forall — verify every element is non-negative after clamping."""

#@ requires \valid(arr, n) and n >= 0
#@ assigns arr[0..n]
#@ ensures \forall i; 0 <= i and i < n ==> arr[i] >= 0
def clamp_nonneg(arr: list, n: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \forall k; 0 <= k and k < i ==> arr[k] >= 0
    #@ loop variant n - i
    while i < n:
        if arr[i] < 0:
            arr[i] = 0
        i = i + 1
    return 0
