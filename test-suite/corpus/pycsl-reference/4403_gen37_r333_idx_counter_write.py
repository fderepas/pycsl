r"""Test 4403 -- gen #37 route #333 (expected FAIL): writing a user local `_idx_i = 10` inside `for i in range(3)` overwrote the generated loop counter (loop exited after one pass) and PROVED `\result == 1` (CPython 3). REFUSED (PYCSL-R327-IDENT-COLLISION, route #333).
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def g(n: int) -> int:
    s = 0
    #@ loop invariant (s == 0 and _idx_i == 0) or (s == 1 and _idx_i == 11)
    for i in range(3):
        s = s + 1
        _idx_i = 10
    return s

if __name__ == "__main__":
    assert g(0) == 1, g(0)
