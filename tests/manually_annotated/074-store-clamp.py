"""Phase 4 store model: clamp all elements to [lo, hi] range."""

#@ requires \valid(arr, n) and n >= 0
#@ assigns arr[0..n]
#@ ensures \result == 0
def clamp_array(arr: list, n: int, lo: int, hi: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        if arr[i] < lo:
            arr[i] = lo
        if arr[i] > hi:
            arr[i] = hi
        i = i + 1
    return 0
