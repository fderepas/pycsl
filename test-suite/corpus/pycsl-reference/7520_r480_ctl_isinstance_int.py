r"""Test 7520 -- route #480 (expected PASS): CONTROL -- `1 if isinstance(n, int) else 0` claiming `\result == 1` (a builtin type as isinstance's class spec). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \result == 1
#@ no_exception \all
def f(n: int) -> int:
    return 1 if isinstance(n, int) else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
