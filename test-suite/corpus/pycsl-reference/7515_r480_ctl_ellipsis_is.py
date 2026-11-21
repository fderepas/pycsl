r"""Test 7515 -- route #480 (expected PASS): CONTROL -- `x = ...; return 1 if x is ... else 0` claiming `\result == 1` (identity of the Ellipsis singleton is reflexive). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \result == 1
def f(n: int) -> int:
    x = ...
    return 1 if x is ... else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
