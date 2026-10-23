r"""Test 1819 — gen #31 FALSE TWIN of 1818: `bytes(2)[0]` is 0, not 1.

Without this file, 1818 would be indistinguishable from a lowering that lets any claim
about a `bytes(n)` element through. CPython: `bytes(2)[0]` is 0.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 1
def f() -> int:
    b = bytes(2)
    return b[0]
