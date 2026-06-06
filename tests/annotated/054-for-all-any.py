""  # pycsl
#@ requires n >= 0
#@ requires n <= \length(arr)
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def all_positive(arr: list, n: int) -> bool:
    i = 0
    acc = 1
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant acc == 1 or acc == 0
    #@ loop variant n - i
    while i < n:
        item = arr[i]
        if item <= 0:
            acc = 0
            i = n
        else:
            i += 1
    return acc


#@ requires n >= 0
#@ requires n <= \length(arr)
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def any_negative(arr: list, n: int) -> bool:
    i = 0
    acc = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant acc == 0 or acc == 1
    #@ loop variant n - i
    while i < n:
        item = arr[i]
        if item < 0:
            acc = 1
            i = n
        else:
            i += 1
    return acc


#@ requires n >= 0
#@ requires n <= \length(arr)
#@ ensures \result == 1 or \result == 0
#@ assigns \nothing
def none_zero(arr: list, n: int) -> int:
    i = 0
    acc = 1
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant acc == 1 or acc == 0
    #@ loop variant n - i
    while i < n:
        item = arr[i]
        if item == 0:
            acc = 0
            i = n
        else:
            i += 1
    return acc
