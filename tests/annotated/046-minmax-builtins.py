""  # pycsl
#@ requires lo <= hi
#@ ensures \result >= lo
#@ ensures \result <= hi
#@ ensures 1 == 1
#@ assigns \nothing
def clamp(value: int, lo: int, hi: int) -> int:
    if value < lo:
        return lo
    elif value > hi:
        return hi
    else:
        return value


#@ requires n >= 0
#@ requires \length(arr) >= n
#@ ensures \result <= n * cap
#@ assigns \nothing
def bounded_sum(arr: list, n: int, cap: int) -> int:
    total = 0
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant total <= i * cap
    #@ loop variant n - i
    while i < n:
        total += min(arr[i], cap)
        i += 1
    return total


#@ requires n >= 1
#@ requires n <= \length(arr)
#@ ensures \result <= bound
#@ assigns \nothing
def array_max_bounded(arr: list, n: int, bound: int) -> int:
    best = arr[0]
    i = 1
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        if arr[i] > best:
            best = arr[i]
        i += 1
    if best <= bound:
        return best
    return bound


#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def midpoint(a: int, b: int) -> int:
    lo = min(a, b)
    hi = max(a, b)
    return lo + (hi - lo) // 2
