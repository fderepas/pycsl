r"""Test 5295 -- gen #37 route #386 (expected FAIL): `[max(1, 2) for max in [min]]`; FAIL at base (a WhyML type error), REFUSED after (comprehension target named like a builtin, route #386).
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 2
#@ assigns \nothing
def m() -> int:
    xs: List[int] = [max(1, 2) for max in [min]]
    return xs[0]


if __name__ == "__main__":
    r = m()
    print("VIOLATION m() =", r) if r != 2 else print("no violation")
