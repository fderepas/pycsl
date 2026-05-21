"""Test 0309 — PyCSL Annotation Reference 11.1.2 — Ghost tuple3 proof"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_ghost_tuple3_proof(n: int) -> int:
    #@ ghost t : tuple3 = \mktuple(0, 0, n)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \proj(t, 0) == i
    #@ loop invariant \proj(t, 2) == n - i
    #@ loop variant n - i
    while i < n:
        #@ ghost t = \mktuple(\proj(t, 0) + 1, \proj(t, 1), \proj(t, 2) - 1)
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_ghost_tuple3_proof(0) == 0
    assert test_ghost_tuple3_proof(4) == 4
    print("PASS")
