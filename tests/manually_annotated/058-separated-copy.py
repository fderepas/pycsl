"""Phase 1 test: \separated with two arrays."""


#@ requires \valid(src, n)
#@ requires \valid(dst, n)
#@ requires \separated(src, n, dst, n)
#@ requires n >= 0
#@ ensures \result == 0
#@ assigns dst[0..n]
def copy_array(src: list, dst: list, n: int) -> int:
    """Copy src[0..n) into dst[0..n).

    \separated(src, n, dst, n) asserts the two regions do not overlap.
    In the Hoare model this is trivially true (value-typed arrays never alias);
    in a heap model it would become a non-trivial separation constraint.
    """
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        dst[i] = src[i]
        i = i + 1
    return 0
