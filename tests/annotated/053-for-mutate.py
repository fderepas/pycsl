""  # pycsl
#@ requires n >= 0
#@ requires n <= \length(arr)
#@ ensures 1 == 1
#@ assigns \nothing
def scale_array(arr: list, n: int, factor: int) -> None:
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        arr[i] = arr[i] * factor
        i += 1


#@ requires n >= 0
#@ requires n <= \length(arr)
#@ requires lo <= hi
#@ ensures 1 == 1
#@ assigns \nothing
def clamp_array(arr: list, n: int, lo: int, hi: int) -> None:
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        if arr[i] < lo:
            arr[i] = lo
        if arr[i] > hi:
            arr[i] = hi
        i += 1
