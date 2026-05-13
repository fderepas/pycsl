"""Phase 3 typed model: negate first element, old(arr[0]) in postcondition."""

#@ requires \valid(arr, n) and n >= 1
#@ ensures arr[0] == 0 - \old(arr[0])
#@ assigns arr[0..1]
def negate_first(arr: list, n: int) -> int:
    arr[0] = 0 - arr[0]
    return 0
