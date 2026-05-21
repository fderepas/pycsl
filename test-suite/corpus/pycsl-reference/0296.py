"""Test 0296 — PyCSL Annotation Reference 7.5 — Ghost set variable"""
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def mark_seen(n: int) -> int:
    #@ ghost seen : ghost_set = \set_empty
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        #@ ghost seen = \set_add(seen, i)
        i = i + 1
    return n


if __name__ == "__main__":
    assert mark_seen(0) == 0
    assert mark_seen(3) == 3
    print("PASS")
