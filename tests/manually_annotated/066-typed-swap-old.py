"""Phase 3 typed model: swap first two elements, old(arr[i]) postcondition."""

#@ requires \valid(arr, n) and n >= 2
#@ ensures arr[0] == \old(arr[1])
#@ ensures arr[1] == \old(arr[0])
#@ assigns arr[0..2]
def swap_first_two(arr: list, n: int) -> int:
    tmp = arr[0]
    arr[0] = arr[1]
    arr[1] = tmp
    return 0
