""  # pycsl
#@ requires n >= 1
#@ requires \length(arr) >= n
#@ ensures \result >= arr[0]
#@ assigns \nothing
def array_max(arr: list, n: int) -> int:
    acc = arr[0]
    i = 1
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant acc >= arr[0]
    #@ loop variant n - i
    while i < n:
        if arr[i] > acc:
            acc = arr[i]
        i += 1
    return acc


#@ requires n >= 1
#@ requires \length(arr) >= n
#@ ensures \result <= arr[0]
#@ assigns \nothing
def array_min(arr: list, n: int) -> int:
    acc = arr[0]
    i = 1
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant acc <= arr[0]
    #@ loop variant n - i
    while i < n:
        if arr[i] < acc:
            acc = arr[i]
        i += 1
    return acc
