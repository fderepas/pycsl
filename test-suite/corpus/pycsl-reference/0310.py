"""Test 0310 — PyCSL Annotation Reference 11.1.3 — Ghost dict Map.get_set proof"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_ghost_dict_proof(n: int) -> int:
    #@ ghost d : ghost_dict = \empty_map
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \map_get(d, 0) == i
    #@ loop variant n - i
    while i < n:
        #@ ghost d = \map_set(d, 0, i + 1)
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_ghost_dict_proof(0) == 0
    assert test_ghost_dict_proof(5) == 5
    print("PASS")
