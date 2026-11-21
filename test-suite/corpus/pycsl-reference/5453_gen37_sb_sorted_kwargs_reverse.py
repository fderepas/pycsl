r"""Test 5453 -- gen #37 systematic rule SB / route #390 (expected FAIL): red team 30 `i13_sorted_kwargs_reverse` -- a `**` mapping passed to a builtin, dropped by the builtin model; PROVED at base 7bf752d4e (CPython: VIOLATION f = [2, 1]). REFUSED (PYCSL-R379-STARRED-CALL-ARGUMENT).
"""
# pycsl-expected: FAIL
from typing import List


#@ requires len(xs) == 2
#@ ensures \result[0] <= \result[1]
def f(xs: List[int]) -> List[int]:
    return sorted(xs, **{"reverse": True})


if __name__ == "__main__":
    r = f([1, 2])
    print("VIOLATION f =", r) if r[0] > r[1] else print("no violation")
