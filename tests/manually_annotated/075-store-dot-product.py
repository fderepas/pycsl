"""Phase 4 store model: dot product of two arrays, store model read-only."""

#@ requires \valid(a, n) and \valid(b, n) and n >= 0
#@ assigns \nothing
#@ ensures 1 == 1
def dot_product(a: list, b: list, n: int) -> int:
    acc = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        acc = acc + a[i] * b[i]
        i = i + 1
    return acc
