r"""Test 4402 -- gen #37 route #333 (expected FAIL): user local `_idx_i = 5` is shadowed by the generated loop counter `_idx_i` of `for i in range(1)`: the body read 0 and PROVED `\result == 0` (CPython 5). REFUSED (PYCSL-R327-IDENT-COLLISION, route #333).
"""
# pycsl-expected: FAIL
#@ ensures \result == 0
#@ assigns \nothing
def g(n: int) -> int:
    _idx_i = 5
    s = 0
    #@ loop invariant s == 0
    for i in range(1):
        s = s + _idx_i
    return s

if __name__ == "__main__":
    assert g(0) == 0, g(0)
