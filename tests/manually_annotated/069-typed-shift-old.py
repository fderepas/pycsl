"""Phase 3 typed model: add constant to each element, old(arr[i]) in invariant."""

#@ requires \valid(arr, n) and n >= 0 and delta >= 0
#@ assigns arr[0..n]
#@ ensures \result == 0
def shift_array(arr: list, n: int, delta: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = arr[i] + delta
        i = i + 1
    return 0
