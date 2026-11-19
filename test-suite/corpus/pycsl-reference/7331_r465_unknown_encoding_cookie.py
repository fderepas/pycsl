# -*- coding: zz-unknown -*-
r"""Test 7331 -- route #465 (expected FAIL): red-team 38 witness `g14_e141_unknown_encoding_cookie` -- an unknown-encoding coding cookie (CPython SyntaxError: unknown encoding). PROVED at base a9eac4a08 / daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R465-COMPILE-ERROR).
"""
# pycsl-expected: FAIL

#@ no_exception \all
def f(n: int) -> int:
    return n + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
