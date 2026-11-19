r"""Test 4622 -- gen #37 route #343 (expected FAIL): NEW latent (adjacent to h05): `range(x)` for `x: Any` under `no_exception \all` lowered to an opaque `py_range_1 x` with no exception VC and PROVED (CPython `m(object())` TypeError). FAIL (PyCSL-R343 assertion: a builtin applied to an erased value under `no_exception`).
"""
# pycsl-expected: FAIL
from typing import Any

#@ no_exception \all
#@ ensures \result == 0
def m(x: Any) -> int:
    r = range(x)
    return 0

if __name__ == "__main__":
    try:
        m(object())
        assert False, "expected TypeError"
    except TypeError:
        pass
