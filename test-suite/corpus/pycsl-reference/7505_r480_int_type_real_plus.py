r"""Test 7505 -- route #480 (expected FAIL): `int.real + n` -- an attribute of the builtin TYPE `int` (a getset descriptor). PROVED at base; CPython TypeError; now REFUSED (R325: derived from the origin `int`).
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return int.real + n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
