r"""Test 7522 -- route #480 (expected PASS): CONTROL -- `1 if n is NotImplemented else 0` under `no_exception \all` (identity against the singleton). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return 1 if n is NotImplemented else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
