"""Phase 3 typed model: copy last element to first, old on distinct indices."""

#@ requires \valid(arr, n) and n >= 2
#@ ensures arr[0] == \old(arr[n - 1])
#@ assigns arr[0..1]
def copy_last_to_first(arr: list, n: int) -> int:
    arr[0] = arr[n - 1]
    return 0
