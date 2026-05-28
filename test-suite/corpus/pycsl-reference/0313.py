"""Test 0313 — PyCSL Annotation Reference 7.2.1 — Ghost array \\make + set proof"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_ghost_array_proof(n: int) -> int:
    #@ ghost snap : array = \make(n, 0)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant i > 0 ==> snap[i - 1] == 1
    #@ loop variant n - i
    while i < n:
        #@ ghost snap[i] = 1
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_ghost_array_proof(0) == 0
    assert test_ghost_array_proof(3) == 3
    print("PASS")
