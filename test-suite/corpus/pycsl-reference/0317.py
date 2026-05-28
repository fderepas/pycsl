# pycsl-expected: FAIL
"""Test 0317 — PyCSL Annotation Reference 11.4.1b — \\proj with non-literal index is rejected"""
_ = 0  # anchor

#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def bad_proj(n: int, i: int) -> int:
    #@ ghost q : tuple2 = \mktuple(0, 0)
    #@ loop invariant \proj(q, i) == 0
    #@ loop variant n
    while n > 0:
        n = n - 1
    return 0

if __name__ == "__main__":
    pass
