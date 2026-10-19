r"""Test 3092 — route #280 (expected FAIL): `t[0].append(1)` on a TUPLE-ELEMENT receiver became
`append_2 (subscript_get !t 0) 1`, an int op with no `writes`; `len(a) == 0` PROVED at
72ab1c57 (red-team p251). CPython: 1. Now refused.
"""
# pycsl-expected: FAIL
from typing import List, Tuple


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: List[int] = []
    t: Tuple[List[int], int] = (a, 1)
    t[0].append(1)
    return len(a)


if __name__ == "__main__":
    assert f() == 1
