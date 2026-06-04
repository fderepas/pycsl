"""Test 0468 — store model: `\separated` makes a disjoint array provably unaffected.

Store-model twin of 0467 over the single global `store` heap.
"""
# pycsl-flags: --memory-model store
_ = 0  # anchor
#@ requires \valid(a, 1)
#@ requires \valid(b, 1)
#@ requires \separated(a, 1, b, 1)
#@ assigns a[0..1]
#@ ensures a[0] == 9
#@ ensures b[0] == \old(b[0])
#@ ensures \result == k
def write_a(a: list, b: list, k: int) -> int:
    a[0] = 9
    return k
