"""Test 0322 — PyCSL Annotation Reference 11.3.5 — Ghost list \\append + \\list_length proof"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_ghost_list_append(n: int) -> int:
    #@ ghost a : ghost_list = \nil
    #@ ghost b : ghost_list = \nil
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \list_length(\append(a, b)) == i
    #@ loop variant n - i
    while i < n:
        #@ ghost a += i
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_ghost_list_append(0) == 0
    assert test_ghost_list_append(4) == 4
    print("PASS")
