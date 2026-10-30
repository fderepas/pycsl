r"""Test 7502 -- route #480 (expected FAIL): `x = len; x += 1` -- a builtin name bound to a local, then augmented. PROVED at base; CPython TypeError; now REFUSED (R325).
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    x = len
    x += 1
    return 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
