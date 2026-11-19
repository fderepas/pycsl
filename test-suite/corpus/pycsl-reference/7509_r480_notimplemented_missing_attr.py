r"""Test 7509 -- route #480 (expected FAIL): `return NotImplemented.zz` -- a missing attribute of the NotImplemented singleton. PROVED at base; CPython AttributeError; now REFUSED (R445).
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return NotImplemented.zz


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
