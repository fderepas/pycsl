"""Phase 5: label before loop body, \at in loop invariant (store model)."""

#@ requires \valid(arr, n) and n >= 0
#@ assigns arr[0..n]
#@ ensures \result == 0
def double_array(arr: list, n: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        #@ label STEP
        arr[i] = arr[i] * 2
        i = i + 1
    return 0
