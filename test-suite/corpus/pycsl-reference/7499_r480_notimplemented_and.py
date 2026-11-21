r"""Test 7499 -- route #480 (expected FAIL): `1 if (NotImplemented and n) else 0` (`and` takes the truth value). PROVED at base; CPython TypeError; now REFUSED (R325).
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return 1 if (NotImplemented and n) else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
