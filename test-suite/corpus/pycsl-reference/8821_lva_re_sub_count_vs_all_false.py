r"""Test 8821 -- lvA re.sub count= (expected FAIL): false twin of 8820. `count=1` replaces only the FIRST
match, so it is NOT the all-occurrences `re.sub`: the model relates `re_sub_count_op` to nothing, and
`\result == True` must NOT prove (CPython: s = "a a" gives "b a" vs "b b").
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re


#@ ensures \result == True
#@ assigns \nothing
def first_equals_all(s: str) -> bool:
    a = re.sub(r"a", "b", s, count=1)
    b = re.sub(r"a", "b", s)
    return a == b


if __name__ == "__main__":
    r = first_equals_all("a a")
    print("VIOLATION contract" if r is not True else "result", r)
