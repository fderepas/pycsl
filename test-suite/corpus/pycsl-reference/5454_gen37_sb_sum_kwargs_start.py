r"""Test 5454 -- gen #37 systematic rule SB / route #390 (expected FAIL): red team 30 `n08_sum_kwargs_start` -- a `**` mapping passed to a builtin, dropped by the builtin model; PROVED at base 7bf752d4e (CPython: VIOLATION f = 13). REFUSED (PYCSL-R379-STARRED-CALL-ARGUMENT).
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 3
def f() -> int:
    return sum([1, 2], **{"start": 10})


if __name__ == "__main__":
    r = f()
    print("VIOLATION f =", r) if r != 3 else print("no violation")
