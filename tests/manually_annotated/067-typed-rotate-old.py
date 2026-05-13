"""Phase 3 typed model: rotate left by one, old(arr[i]) for all positions."""

#@ requires \valid(arr, n) and n >= 2
#@ ensures arr[n - 1] == \old(arr[0])
#@ assigns arr[0..n]
def rotate_left(arr: list, n: int) -> int:
    tmp = arr[0]
    i = 0
    #@ loop invariant 0 <= i and i <= n - 1
    #@ loop variant n - 1 - i
    while i < n - 1:
        arr[i] = arr[i + 1]
        i = i + 1
    arr[n - 1] = tmp
    return 0
