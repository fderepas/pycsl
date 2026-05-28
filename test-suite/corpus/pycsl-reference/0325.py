"""Test 0325 — PyCSL Annotation Reference 11.2.3b — Ghost set \\set_card bounded range proof"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_ghost_set_card(n: int) -> int:
    #@ ghost s : ghost_set = \set_empty
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \set_card(s, 0, i) == i
    #@ loop variant n - i
    while i < n:
        #@ ghost s += i
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_ghost_set_card(0) == 0
    assert test_ghost_set_card(4) == 4
    print("PASS")
