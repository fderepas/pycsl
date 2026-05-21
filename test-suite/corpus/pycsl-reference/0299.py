"""Test 0299 — PyCSL Annotation Reference 11.2 — Ghost set union/inter/diff"""
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def test_set_ops(n: int) -> int:
    #@ ghost s1 : ghost_set = \set_empty
    #@ ghost s2 : ghost_set = \set_empty
    #@ ghost s1 = \set_add(s1, 1)
    #@ ghost s2 = \set_add(s2, 2)
    #@ loop invariant 0 <= n - n and n - n <= n
    #@ loop variant n
    return n
