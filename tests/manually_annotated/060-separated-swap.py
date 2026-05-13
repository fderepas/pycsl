"""Phase 1 test: \valid + \separated for an in-place swap of two arrays."""


#@ requires \valid(a, n)
#@ requires \valid(b, n)
#@ requires \separated(a, n, b, n)
#@ requires n > 0
#@ ensures \result == 0
#@ assigns a[0..n], b[0..n]
def swap_arrays(a: list, b: list, n: int) -> int:
    """Swap a[0..n) and b[0..n) element-by-element.

    \separated(a, n, b, n) asserts no aliasing between the two regions.
    In a heap model this is essential for correctness; in the Hoare model
    it reduces to `true` but is preserved in the IR for future use.
    """
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        tmp = a[i]
        a[i] = b[i]
        b[i] = tmp
        i = i + 1
    return 0
