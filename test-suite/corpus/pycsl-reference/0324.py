"""Test 0324 — PyCSL Annotation Reference 11.2.4d — Ghost dict \\has_key with positive sentinel"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_ghost_has_key_sentinel(n: int) -> int:
    #@ ghost d : ghost_dict = \empty_map
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant i > 0 ==> \has_key(d, 1)
    #@ loop invariant \map_get(d, 1) == i
    #@ loop variant n - i
    while i < n:
        #@ ghost d = \map_set(d, 1, i + 1)
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_ghost_has_key_sentinel(0) == 0
    assert test_ghost_has_key_sentinel(3) == 3
    print("PASS")
