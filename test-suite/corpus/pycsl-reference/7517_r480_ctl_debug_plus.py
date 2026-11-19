r"""Test 7517 -- route #480 (expected PASS): CONTROL -- `__debug__ + n` under `no_exception \all` (`__debug__` is a bool: known int). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return __debug__ + n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
