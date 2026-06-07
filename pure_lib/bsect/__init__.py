# pure_lib/bsect — pure-Python bisect module
# Modelled: classic binary search, body-level provable.


#@ requires 0 <= lo
#@ requires lo <= hi
#@ requires hi <= \length(a)
#@ ensures lo <= \result
#@ ensures \result <= hi
def bisect_left(a, x, lo, hi) -> int:
    #@ loop invariant lo <= low
    #@ loop invariant low <= high
    #@ loop invariant high <= hi
    #@ loop variant high - low
    low = lo
    high = hi
    while low < high:
        mid = (low + high) // 2
        if a[mid] < x:
            low = mid + 1
        else:
            high = mid
    return low
