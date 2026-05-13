"""Quantifier test: \forall in a precondition — sum of non-negative elements."""

#@ requires \valid(arr, n) and n >= 0
#@ requires \forall k; 0 <= k and k < n ==> arr[k] >= 0
#@ assigns \nothing
#@ ensures \result >= 0
def sum_nonneg(arr: list, n: int) -> int:
    i = 0
    total = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant total >= 0
    #@ loop variant n - i
    while i < n:
        total = total + arr[i]
        i = i + 1
    return total
