"""Test 0300 — PyCSL Annotation Reference 11.2 — Ghost list += shorthand and ghost dict += mktuple"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def test_aug_shorthands(n: int) -> int:
    #@ ghost log : ghost_list = \nil
    #@ ghost freq : ghost_dict = \empty_map
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        #@ ghost log += i
        #@ ghost freq += \mktuple(i, 1)
        i = i + 1
    return i
