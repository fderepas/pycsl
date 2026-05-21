"""Test 0295 — PyCSL Annotation Reference 7.4 — Ghost list variable"""
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def collect(n: int) -> int:
    #@ ghost log : ghost_list = \nil
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        #@ ghost log = \cons(i, log)
        i = i + 1
    return n


if __name__ == "__main__":
    assert collect(0) == 0
    assert collect(4) == 4
    print("PASS")
