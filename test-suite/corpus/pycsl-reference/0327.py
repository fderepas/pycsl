"""Test 0327 — PyCSL Annotation Reference 11.6.1"""
""  # pycsl
# \copy_range(arr, lo, hi) — bounded array snapshot into a ghost array.
# Lowers to Array.sub arr lo (hi - lo) in Why3.

#@ requires \length(arr) >= n and n >= 0
#@ ensures \result == n
#@ assigns \nothing
def copy_range_basic(arr: list, n: int) -> int:
    #@ ghost snap : array = \copy_range(arr, 0, n)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \forall j; 0 <= j and j < i ==> snap[j] == arr[j]
    #@ loop variant n - i
    while i < n:
        i += 1
    return i


if __name__ == "__main__":
    assert copy_range_basic([1, 2, 3, 4, 5], 3) == 3
    assert copy_range_basic([], 0) == 0
