"""Test 0318 — PyCSL Annotation Reference 11.3.4 — Ghost list \\list_length proof"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_ghost_list_length(n: int) -> int:
    #@ ghost log : ghost_list = \nil
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \list_length(log) == i
    #@ loop variant n - i
    while i < n:
        #@ ghost log += i
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_ghost_list_length(0) == 0
    assert test_ghost_list_length(4) == 4
    print("PASS")
