"""Phase 5: label PRE before a write; ensures preserves second element via \at."""

#@ requires \valid(arr, n) and n >= 2
#@ ensures arr[1] == \at(arr[1], PRE)
#@ assigns arr[0..1]
def overwrite_first(arr: list, n: int, v: int) -> int:
    #@ label PRE
    arr[0] = v
    return 0
