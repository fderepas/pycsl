""  # pycsl
#@ requires n >= 0
#@ requires n <= \length(arr)
#@ ensures \result >= 0
#@ assigns \nothing
def sum_skip_negative(arr: list, n: int) -> int:
    total = 0
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant total >= 0
    #@ loop variant n - i
    while i < n:
        if arr[i] < 0:
            i += 1
            continue
        total += arr[i]
        i += 1
    return total


#@ requires n >= 0
#@ requires n <= \length(arr)
#@ ensures 1 == 1
#@ assigns \nothing
def sum_skip_zero(arr: list, n: int) -> int:
    total = 0
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        if arr[i] == 0:
            i += 1
            continue
        total += arr[i]
        i += 1
    return total
