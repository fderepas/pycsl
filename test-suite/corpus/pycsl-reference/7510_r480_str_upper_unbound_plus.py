r"""Test 7510 -- route #480 (expected FAIL): `str.upper + n` -- an unbound method of a builtin type. PROVED at base; CPython TypeError; now REFUSED (R325).
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return str.upper + n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
