"""Test 0312 — PyCSL Annotation Reference 11.3.2 — Ghost list \\nth proof"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_ghost_list_nth(n: int) -> int:
    #@ ghost log : ghost_list = \nil
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant i > 0 ==> \nth(log, 0) == i - 1
    #@ loop variant n - i
    while i < n:
        #@ ghost log += i
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_ghost_list_mem(0) == 0
    assert test_ghost_list_mem(4) == 4
    print("PASS")
