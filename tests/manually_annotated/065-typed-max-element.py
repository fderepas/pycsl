"""Phase 2 typed model: find maximum element with \valid."""

#@ requires \valid(arr, n) and n >= 1
#@ assigns \nothing
#@ ensures \result >= arr[0]
def max_element(arr: list, n: int) -> int:
    m = arr[0]
    i = 1
    #@ loop invariant 1 <= i and i <= n and m >= arr[0]
    #@ loop variant n - i
    while i < n:
        if arr[i] > m:
            m = arr[i]
        i = i + 1
    return m
