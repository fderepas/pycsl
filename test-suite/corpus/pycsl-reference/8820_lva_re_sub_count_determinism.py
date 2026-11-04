r"""Test 8820 -- lvA re.sub count= (expected PASS): `re.sub(<pat>, <str repl>, <str>, count=<int literal>)`
lowers to the law-free DETERMINISTIC `val function re_sub_count_op (pat rep s: string) (count: int) : string`
(CPython: a pure function of its four arguments). Equal arguments give equal results. At base the
`count=` keyword kept the opaque-int lowering and the claim was refused (R325). Twin: 8821 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import re


#@ ensures \result == True
#@ assigns \nothing
def same_twice(s: str) -> bool:
    a = re.sub(r"a+", "b", s, count=1)
    b = re.sub(r"a+", "b", s, count=1)
    return a == b


if __name__ == "__main__":
    for s in ["", "a", "aab aa", "xyz"]:
        r = same_twice(s)
        print("VIOLATION contract" if r is not True else "result", r)
