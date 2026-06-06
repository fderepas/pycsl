""  # pycsl
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def for_sum(arr: list, n: int) -> int:
    m = len(arr)
    total = 0
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= m
    #@ loop variant m - i
    while i < m:
        total += arr[i]
        i += 1
    return total


#@ requires n >= 0
#@ requires n <= \length(arr)
#@ ensures 1 == 1
#@ assigns \nothing
def for_product(arr: list, n: int) -> int:
    acc = 1
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        acc *= arr[i]
        i += 1
    return acc
