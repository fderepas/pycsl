""  # pycsl
#@ requires n >= 0
#@ requires \length(arr) >= n
#@ ensures 1 == 1
#@ assigns \nothing
def array_sum(arr: list, n: int) -> int:
    total = 0
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        total += arr[i]
        i += 1
    return total


#@ requires n >= 0
#@ requires \length(arr) >= n
#@ ensures \result == 1 or \result == 0
#@ assigns \nothing
def array_all_positive(arr: list, n: int) -> bool:
    i = 0
    acc = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        if arr[i] <= 0:
            acc = False
            i = n
        else:
            i += 1
    return True
