"""Phase 5: label PRE, postcondition uses \at(arr[0], PRE) in typed model."""

#@ requires \valid(arr, n) and n >= 1
#@ ensures arr[0] == \at(arr[0], PRE) + 1
#@ assigns arr[0..1]
def increment_first(arr: list, n: int) -> int:
    #@ label PRE
    arr[0] = arr[0] + 1
    return 0
