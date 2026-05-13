"""Phase 4 store model: accumulate prefix sums into a destination array."""

#@ requires \valid(src, n) and \valid(dst, n) and n >= 0
#@ requires \separated(src, n, dst, n)
#@ assigns dst[0..n]
#@ ensures \result == 0
def prefix_sum(src: list, dst: list, n: int) -> int:
    i = 0
    acc = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        acc = acc + src[i]
        dst[i] = acc
        i = i + 1
    return 0
