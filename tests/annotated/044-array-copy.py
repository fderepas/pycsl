""  # pycsl
#@ requires n >= 0
#@ requires \length(src) >= n
#@ requires \length(dst) >= n
#@ ensures 1 == 1
#@ assigns \nothing
def copy_array(src: list, dst: list, n: int) -> None:
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        dst[i] = src[i]
        i += 1


#@ requires n >= 0
#@ requires \length(src) >= n
#@ requires \length(dst) >= n
#@ ensures 1 == 1
#@ assigns \nothing
def copy_reverse(src: list, dst: list, n: int) -> int:
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        dst[i] = src[n - 1 - i]
        i += 1
    return 0
