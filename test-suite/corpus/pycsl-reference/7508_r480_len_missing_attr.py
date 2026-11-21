r"""Test 7508 -- route #480 (expected FAIL): `return len.zz` -- a missing attribute of a builtin function. PROVED at base; CPython AttributeError; now REFUSED (PYCSL-R445-ATTRIBUTE-NOT-DEFINED, judged on the real builtin object).
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return len.zz


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
