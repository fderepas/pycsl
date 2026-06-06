""  # pycsl
#@ requires n >= 0
#@ requires \length(src) >= n
#@ requires \length(dst) >= n
#@ ensures 1 == 1
#@ assigns \nothing
#@ requires n <= \length(src)
#@ requires n <= \length(dst)
def prefix_sum(src: list, dst: list, n: int) -> None:
    acc = 0
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        acc += src[i]
        dst[i] = acc
        i += 1


#@ requires n >= 1
#@ requires \length(src) >= n
#@ requires \length(dst) >= n
#@ assigns \nothing
#@ ensures 1 == 1
#@ requires n >= 0
#@ requires n <= \length(src)
#@ requires n <= \length(dst)
def running_max(src: list, dst: list, n: int) -> None:
    best = src[0]
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        if src[i] > best:
            best = src[i]
        dst[i] = best
        i += 1
