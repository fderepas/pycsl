r"""Test 7500 -- route #480 (expected FAIL): `1 if any([NotImplemented]) else 0` (`any` takes each element's truth value). PROVED at base; CPython TypeError; now REFUSED (R325).
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return 1 if any([NotImplemented]) else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
