"""Phase 5: two labels, POST captures state after first mutation."""

#@ requires \valid(arr, n) and n >= 2
#@ ensures arr[0] == \at(arr[0], PRE) + arr[1]
#@ assigns arr[0..1]
def accumulate_first(arr: list, n: int) -> int:
    #@ label PRE
    arr[0] = arr[0] + arr[1]
    return 0
