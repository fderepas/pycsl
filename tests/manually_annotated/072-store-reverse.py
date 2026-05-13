"""Phase 4 store model: reverse an array in place using separated regions."""

#@ requires \valid(arr, n) and n >= 0
#@ assigns arr[0..n]
#@ ensures \result == 0
def reverse_array(arr: list, n: int) -> int:
    lo = 0
    hi = n - 1
    #@ loop invariant 0 <= lo and lo <= hi + 1 and hi < n
    #@ loop variant hi - lo
    while lo < hi:
        tmp = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = tmp
        lo = lo + 1
        hi = hi - 1
    return 0
