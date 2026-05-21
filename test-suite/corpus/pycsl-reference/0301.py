"""Test 0301 — PyCSL Annotation Reference 11.2 — Ghost set += shorthand"""
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def test_set_aug(n: int) -> int:
    #@ ghost seen : ghost_set = \set_empty
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        #@ ghost seen += i
        i = i + 1
    return i
