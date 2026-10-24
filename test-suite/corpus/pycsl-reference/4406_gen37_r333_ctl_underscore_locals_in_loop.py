r"""Test 4406 -- gen #37 route #333 (control, expected PASS): control: user locals `_i`, `_r`, `idx_i` beside `for i in range(3)` are outside the generated-binder namespace (`_idx_*`); `_r` is the name of a CLOSED generated match binder and stays accepted. PROVED.
"""
# pycsl-expected: PASS
#@ ensures \result == 8
#@ assigns \nothing
def g(n: int) -> int:
    _i = 5
    idx_i = 0
    _r = 0
    #@ loop invariant _r == 0 and idx_i == 0 and _i == 5
    for i in range(3):
        _r = _r + 0
    return _i + 3 + idx_i + _r

if __name__ == "__main__":
    assert g(0) == 8, g(0)
