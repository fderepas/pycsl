# -*- coding: utf-8 -*-
r"""Advice probe for route #465 (make the coding cookie match the encoding), from test 7330 -- route #465 (expected FAIL): red-team 38 witness `g14_e140_ascii_cookie_nonascii_comment` -- an `ascii` coding cookie over a non-ASCII comment (CPython SyntaxError: encoding problem). PROVED at base a9eac4a08 / daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R465-COMPILE-ERROR).
"""
# pycsl-expected: PASS
# café

#@ no_exception \all
def f(n: int) -> int:
    return n + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
