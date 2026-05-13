"""Phase 2 typed model: scale every element by a factor."""

#@ requires \valid(arr, n) and n >= 0 and factor >= 0
#@ assigns arr[0..n]
#@ ensures \result == 0
def scale_array(arr: list, n: int, factor: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = arr[i] * factor
        i = i + 1
    return 0
