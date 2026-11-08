r"""Test 5455 -- gen #37 systematic rule SB (expected FAIL): NEW shape: `max(*xs)` -- a `*` sequence to a builtin (the model reads explicit arguments only); ill-typed at base 7bf752d4e (L3-tc, fail-closed); REFUSED (PYCSL-R379-STARRED-CALL-ARGUMENT). CPython 3.
"""
# pycsl-expected: FAIL
from typing import List

#@ requires len(xs) == 2
#@ ensures \result == xs[0]
def f(xs: List[int]) -> int:
    return max(*xs)

if __name__ == "__main__":
    print(f([1, 3]))
