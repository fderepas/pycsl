""  # pycsl
#@ requires n >= 0
#@ requires \length(arr) >= n
#@ ensures 1 == 1
#@ assigns \nothing
def fill_zeros(arr: list, n: int) -> None:
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = 0
        i += 1


#@ requires n >= 0
#@ requires \length(arr) >= n
#@ ensures 1 == 1
#@ assigns \nothing
def fill_value(arr: list, n: int, v: int) -> int:
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = v
        i += 1
    return 0
