"""Phase 2 typed model: fill array with zeros, full frame condition."""

#@ requires \valid(arr, n) and n >= 0
#@ assigns arr[0..n]
#@ ensures \forall i; 0 <= i and i < n ==> \result == 0
def fill_zeros(arr: list, n: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = 0
        i = i + 1
    return 0
