"""Phase 1 test: \valid precondition with a loop over an array."""


#@ requires \valid(arr, n)
#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def sum_nonneg(arr: list, n: int) -> int:
    """Sum non-negative elements in arr[0..n).

    \valid(arr, n) asserts n <= length(arr), so arr[i] is in-bounds for i < n.
    """
    total = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant total >= 0
    #@ loop variant n - i
    while i < n:
        if arr[i] >= 0:
            total = total + arr[i]
        i = i + 1
    return total
