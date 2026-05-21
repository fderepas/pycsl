"""Test 0294 — PyCSL Annotation Reference 7.3 — Ghost dict variable"""
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def accumulate(n: int) -> int:
    #@ ghost freq : ghost_dict = \empty_map
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        #@ ghost freq = \map_set(freq, i, i)
        i = i + 1
    return n


if __name__ == "__main__":
    assert accumulate(0) == 0
    assert accumulate(5) == 5
    print("PASS")
