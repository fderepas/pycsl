""  # pycsl
#@ requires 1 == 1
#@ requires n >= 0
#@ requires n <= \length(arr)
#@ ensures \result >= 0
#@ ensures \result <= \length(arr)
#@ assigns \nothing
def count_positive(arr: list, n: int) -> int:
    count = 0
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant count >= 0
    #@ loop invariant count <= i
    #@ loop variant n - i
    while i < n:
        if arr[i] > 0:
            count += 1
        i += 1
    return count


#@ requires \length(arr) == n
#@ requires lo <= hi
#@ ensures \result >= 0
#@ ensures \result <= n
#@ assigns \nothing
#@ requires n >= 0
#@ requires n <= \length(arr)
def count_in_range(arr: list, n: int, lo: int, hi: int) -> int:
    count = 0
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant count >= 0
    #@ loop invariant count <= i
    #@ loop variant n - i
    while i < n:
        if arr[i] >= lo and arr[i] <= hi:
            count += 1
        i += 1
    return count
