"""Phase 4 store model: fill array with a constant value."""

#@ requires \valid(arr, n) and n >= 0 and value >= 0
#@ assigns arr[0..n]
#@ ensures \result == 0
def fill_value(arr: list, n: int, value: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = value
        i = i + 1
    return 0
