"""Quantifier test: \forall + \exists combined — all values in [lo, hi]
implies there exists an element equal to lo (pigeonhole-style precondition)."""

#@ requires \valid(arr, n) and n >= 1
#@ requires \forall i; 0 <= i and i < n ==> arr[i] >= lo and arr[i] <= hi
#@ requires \exists j; 0 <= j and j < n and arr[j] == lo
#@ assigns \nothing
#@ ensures \result >= lo and \result <= hi
def find_min_in_range(arr: list, n: int, lo: int, hi: int) -> int:
    m = arr[0]
    i = 1
    #@ loop invariant 1 <= i and i <= n
    #@ loop invariant m >= lo and m <= hi
    #@ loop variant n - i
    while i < n:
        if arr[i] < m:
            m = arr[i]
        i = i + 1
    return m
