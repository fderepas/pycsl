r"""Test 7494 -- route #479 (expected FAIL): `...` as a ternary VALUE compared `== 0` (`(1 if n > 5 else ...) == 0`), claiming `\result == 1`. PROVED at base; CPython returns 0; now FAILS.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires n == 0
#@ ensures \result == 1
def f(n: int) -> int:
    return 1 if (1 if n > 5 else ...) == 0 else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
