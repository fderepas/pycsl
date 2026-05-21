"""Test 0308 — PyCSL Annotation Reference 11.2.7 — Ghost set \\set_union with \\set_mem (proof)"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_set_union_mem(n: int) -> int:
    #@ ghost s1 : ghost_set = \set_empty
    #@ ghost s2 : ghost_set = \set_empty
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant i > 0 ==> \set_mem(i - 1, s1)
    #@ loop invariant i > 0 ==> \set_mem(i - 1, \set_union(s1, s2))
    #@ loop variant n - i
    while i < n:
        #@ ghost s1 += i
        #@ ghost s2 += i
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_set_union_mem(0) == 0
    assert test_set_union_mem(3) == 3
    print("PASS")
