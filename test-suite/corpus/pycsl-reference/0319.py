"""Test 0319 — PyCSL Annotation Reference 11.1.4 — Ghost tuple4 \\proj proof"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_ghost_tuple4(n: int) -> int:
    #@ ghost t : tuple4 = \mktuple(0, 0, 0, 0)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \proj(t, 0) == i
    #@ loop invariant \proj(t, 1) == i
    #@ loop invariant \proj(t, 2) == i
    #@ loop invariant \proj(t, 3) == i
    #@ loop variant n - i
    while i < n:
        #@ ghost t = \mktuple(i + 1, i + 1, i + 1, i + 1)
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_ghost_tuple4(0) == 0
    assert test_ghost_tuple4(3) == 3
    print("PASS")
