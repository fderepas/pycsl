"""Test 0323 — PyCSL Annotation Reference 11.2.8 — Ghost set \\set_eq proof"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_ghost_set_eq(n: int) -> int:
    #@ ghost s1 : ghost_set = \set_empty
    #@ ghost s2 : ghost_set = \set_empty
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \set_eq(s1, s2)
    #@ loop variant n - i
    while i < n:
        #@ ghost s1 += i
        #@ ghost s2 += i
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_ghost_set_eq(0) == 0
    assert test_ghost_set_eq(3) == 3
    print("PASS")
