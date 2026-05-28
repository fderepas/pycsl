"""Test 0330 — PyCSL Annotation Reference 11.9.1"""
_ = 0  # anchor
# Demonstrates \map_remove and option-type \has_key fix:
# \has_key is true for a key with stored value 0 (unlike the old sentinel-0 convention
# where a stored 0 was indistinguishable from absent).

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def map_remove_proof(n: int) -> int:
    #@ ghost d : ghost_dict = \empty_map
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant i > 0 ==> \has_key(d, 1)
    #@ loop invariant i > 0 ==> \map_get(d, 1) == 0
    #@ loop variant n - i
    while i < n:
        #@ ghost d = \map_set(d, 0, i + 1)
        #@ ghost d = \map_remove(d, 0)
        #@ ghost d = \map_set(d, 1, 0)
        i = i + 1
    return i


if __name__ == "__main__":
    assert map_remove_proof(0) == 0
    assert map_remove_proof(3) == 3
    print("PASS")
