"""PyCSL mock for Python's bisect module — real binary-search implementations (no \trusted).

The search functions are genuine bisection loops over a list `a`, body-verified to return an
insertion point within `[lo, hi]`. The actual array insert performed by `insort_*` is a runtime
side effect that is not modelled; the verified part is the position computation."""
_ = 0  # anchor


# cite: https://docs.python.org/3/library/bisect.html#bisect.bisect_left
#@ requires lo >= 0
#@ requires hi >= lo
#@ requires \length(a) >= hi
#@ ensures \result >= lo
#@ ensures \result <= hi
def bisect_left(a: list, x: int, lo: int, hi: int) -> int:
    """Leftmost insertion point for x in the sorted slice a[lo:hi]."""
    left = lo
    right = hi
    #@ loop invariant lo <= left and left <= right and right <= hi
    #@ loop variant right - left
    while left < right:
        mid = (left + right) // 2
        if a[mid] < x:
            left = mid + 1
        else:
            right = mid
    return left


# cite: https://docs.python.org/3/library/bisect.html#bisect.bisect_right
#@ requires lo >= 0
#@ requires lo <= hi
#@ requires \length(a) >= hi
#@ ensures \result >= lo
#@ ensures \result <= hi
def bisect_right(a: list, x: int, lo: int, hi: int) -> int:
    """Rightmost insertion point for x in the sorted slice a[lo:hi]."""
    left = lo
    right = hi
    #@ loop invariant lo <= left and left <= right and right <= hi
    #@ loop variant right - left
    while left < right:
        mid = (left + right) // 2
        if x < a[mid]:
            right = mid
        else:
            left = mid + 1
    return left


# cite: https://docs.python.org/3/library/bisect.html#bisect.insort_left
#@ requires lo >= 0
#@ requires hi >= lo
#@ requires \length(a) >= hi
#@ ensures \result >= lo
#@ ensures \result <= hi
def insort_left(a: list, x: int, lo: int, hi: int) -> int:
    """Locate the left insertion point (array insert is an unmodelled side effect)."""
    return bisect_left(a, x, lo, hi)


# cite: https://docs.python.org/3/library/bisect.html#bisect.insort_right
#@ requires lo >= 0
#@ requires hi >= lo
#@ requires \length(a) >= hi
#@ ensures \result >= lo
#@ ensures \result <= hi
def insort_right(a: list, x: int, lo: int, hi: int) -> int:
    """Locate the right insertion point (array insert is an unmodelled side effect)."""
    return bisect_right(a, x, lo, hi)
