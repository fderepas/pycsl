""  # pycsl
#@ requires \length(arr) >= 1
#@ ensures \result >= arr[0]
#@ assigns \nothing
#@ requires n >= 0
#@ requires n <= \length(arr)
def for_max(arr: list, n: int) -> int:
    best = arr[0]
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant best >= arr[0]
    #@ loop variant n - i
    while i < n:
        if arr[i] > best:
            best = arr[i]
        i += 1
    return best


#@ requires \length(arr) >= 1
#@ ensures \result <= arr[0]
#@ assigns \nothing
def for_min(arr: list, n: int) -> int:
    best = arr[0]
    i = 0
    m = len(arr)
    #@ loop invariant 0 <= i
    #@ loop invariant i <= m
    #@ loop invariant best <= arr[0]
    #@ loop variant m - i
    while i < m:
        if arr[i] < best:
            best = arr[i]
        i += 1
    return best
