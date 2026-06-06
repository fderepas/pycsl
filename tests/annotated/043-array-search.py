""  # pycsl
#@ requires n >= 0
#@ requires \length(arr) >= n
#@ ensures \result >= -1
#@ ensures \result < n
#@ assigns \nothing
def linear_search(arr: list, n: int, target: int) -> int:
    i = 0
    found = -1
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant found >= -1
    #@ loop invariant found < n
    #@ loop variant n - i
    while i < n:
        if arr[i] == target:
            found = i
            i = n
        else:
            i += 1
    return found


#@ requires n >= 0
#@ requires \length(arr) >= n
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def contains(arr: list, n: int, target: int) -> bool:
    i = 0
    acc = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        if arr[i] == target:
            acc = True
            i = n
        else:
            i += 1
    return False
