"""Phase 2 typed model: sum array elements with \valid precondition."""

#@ requires \valid(arr, n) and n >= 0
#@ assigns \nothing
#@ ensures 1 == 1
def sum_array(arr: list, n: int) -> int:
    s = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        s = s + arr[i]
        i = i + 1
    return s
