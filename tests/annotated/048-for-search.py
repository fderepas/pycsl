""  # pycsl
#@ requires 1 == 1
#@ ensures \result >= -1
#@ ensures \result < \length(arr)
#@ assigns \nothing
def for_search(arr: list, n: int, target: int) -> int:
    n_arr = len(arr)
    idx = 0
    found = -1
    #@ loop invariant 0 <= idx
    #@ loop invariant idx <= n_arr
    #@ loop invariant found >= -1
    #@ loop invariant found < n_arr
    #@ loop variant n_arr - idx
    while idx < n_arr:
        if arr[idx] == target:
            found = idx
            idx = n_arr
        else:
            idx += 1
    return found


#@ requires n == \length(arr)
#@ ensures \result >= -1
#@ ensures \result < n
#@ assigns \nothing
#@ requires n >= 0
#@ requires n <= \length(arr)
def for_last_occurrence(arr: list, n: int, target: int) -> int:
    acc = -1
    idx = 0
    #@ loop invariant 0 <= idx
    #@ loop invariant idx <= n
    #@ loop invariant acc >= -1
    #@ loop invariant acc < n
    #@ loop variant n - idx
    while idx < n:
        item = arr[idx]
        if item == target:
            acc = idx
        idx += 1
    return acc
