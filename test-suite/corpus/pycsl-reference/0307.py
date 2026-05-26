"""Test 0307 — PyCSL Annotation Reference 11.2.6 — Ghost dict \\map_eq in loop invariant (proof)"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_map_eq_invariant(n: int) -> int:
    #@ ghost d1 : ghost_dict = \empty_map
    #@ ghost d2 : ghost_dict = \empty_map
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \map_eq(d1, d2)
    #@ loop variant n - i
    while i < n:
        #@ ghost d1 = \map_set(d1, i, i)
        #@ ghost d2 = \map_set(d2, i, i)
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_map_eq_invariant(0) == 0
    assert test_map_eq_invariant(3) == 3
    print("PASS")
