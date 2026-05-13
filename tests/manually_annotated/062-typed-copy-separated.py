"""Phase 2 typed model: copy src into dst with \separated and \old."""

#@ requires \valid(src, n) and \valid(dst, n) and n >= 0
#@ requires \separated(src, n, dst, n)
#@ assigns dst[0..n]
#@ ensures \result == 0
def copy_array(src: list, dst: list, n: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        dst[i] = src[i]
        i = i + 1
    return 0
