r"""Test 3082 — route #279 (expected FAIL): REBINDING an already-declared list name to another list
(`b = a` after `b` was built) is `b := !a`, a copy; route #81's fence skipped declared names, so
`len(a) == 1` PROVED at 72ab1c57 after `b.append(2)`. CPython: 2. Now refused.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: List[int] = [1]
    b: List[int] = []
    b.append(5)
    b = a
    b.append(2)
    return len(a)


if __name__ == "__main__":
    assert f() == 2
