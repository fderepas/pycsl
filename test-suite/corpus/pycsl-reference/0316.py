"""Test 0316 — PyCSL Annotation Reference 11.5 — Multi-ghost-type: dict + list + set simultaneously"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_multi_ghost(n: int) -> int:
    #@ ghost d : ghost_dict = \empty_map
    #@ ghost log : ghost_list = \nil
    #@ ghost seen : ghost_set = \set_empty
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \map_get(d, 0) == i
    #@ loop invariant i > 0 ==> \nth(log, 0) == 0
    #@ loop variant n - i
    while i < n:
        #@ ghost d = \map_set(d, 0, i + 1)
        #@ ghost log += 0
        #@ ghost seen += i
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_multi_ghost(0) == 0
    assert test_multi_ghost(3) == 3
    print("PASS")
