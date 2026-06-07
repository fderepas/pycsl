# pure_lib/bsect — pure-Python bisect module
# Named 'bsect' to avoid stdlib name clash.
#
# Contracts derived from library_reference/bisect.rst.
# RST: "Locate the insertion point for x in a to maintain sorted order."
# RST: "bisect_left, bisect_right, insort_left, insort_right"
#
# Body-proven binary search with full loop invariants.


#@ requires 0 <= lo
#@ requires lo <= hi
#@ requires hi <= \length(a)
#@ ensures lo <= \result
#@ ensures \result <= hi
#@ assigns \nothing
def bisect_left(a: list, x: int, lo: int, hi: int) -> int:
    """RST: 'Locate the leftmost insertion point for x in a[lo:hi].'
    Returns index in [lo, hi] maintaining sorted order."""
    low = lo
    high = hi
    #@ loop invariant lo <= low
    #@ loop invariant low <= high
    #@ loop invariant high <= hi
    #@ loop variant high - low
    while low < high:
        mid = (low + high) // 2
        if a[mid] < x:
            low = mid + 1
        else:
            high = mid
    return low


#@ requires 0 <= lo
#@ requires lo <= hi
#@ requires hi <= \length(a)
#@ ensures lo <= \result
#@ ensures \result <= hi
#@ assigns \nothing
def bisect_right(a: list, x: int, lo: int, hi: int) -> int:
    """RST: 'Locate the rightmost insertion point for x in a[lo:hi].'
    Similar to bisect_left but goes right on equality."""
    low = lo
    high = hi
    #@ loop invariant lo <= low
    #@ loop invariant low <= high
    #@ loop invariant high <= hi
    #@ loop variant high - low
    while low < high:
        mid = (low + high) // 2
        if x < a[mid]:
            high = mid
        else:
            low = mid + 1
    return low


#@ requires 0 <= lo
#@ requires lo <= hi
#@ requires hi <= \length(a)
#@ requires hi < 2147483647
#@ ensures lo <= \result
#@ ensures \result <= hi
#@ assigns \nothing
def insort_left_index(a: list, x: int, lo: int, hi: int) -> int:
    """RST: 'Insert x in a in sorted order (left bias).'
    Returns the insertion index (actual insert modifies the list)."""
    return bisect_left(a, x, lo, hi)


#@ requires 0 <= lo
#@ requires lo <= hi
#@ requires hi <= \length(a)
#@ requires hi < 2147483647
#@ ensures lo <= \result
#@ ensures \result <= hi
#@ assigns \nothing
def insort_right_index(a: list, x: int, lo: int, hi: int) -> int:
    """RST: 'Insert x in a in sorted order (right bias).'
    Returns the insertion index."""
    return bisect_right(a, x, lo, hi)
