"""Test 0305 — PyCSL Annotation Reference 11.1.1 — Ghost tuple2 proof"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_ghost_tuple_proof(n: int) -> int:
    #@ ghost p : tuple2 = \mktuple(0, n)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \fst(p) == i
    #@ loop invariant \snd(p) == n - i
    #@ loop variant n - i
    while i < n:
        #@ ghost p = \mktuple(\fst(p) + 1, \snd(p) - 1)
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_ghost_tuple_proof(0) == 0
    assert test_ghost_tuple_proof(5) == 5
    print("PASS")
