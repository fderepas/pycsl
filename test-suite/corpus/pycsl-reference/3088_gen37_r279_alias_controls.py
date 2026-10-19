r"""Test 3088 — route #279 CONTROLS (expected PASS): an element STORE through a plain list alias is
faithful (the array model shares the array); an alias killed by a rebind before the mutation
(`b = a; b = []; b.append(i)` in a loop) is no alias; a read-only alias is a copy no one can
tell apart. All three must keep proving after the repair.
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \result == 9
#@ assigns \nothing
def store_through_alias() -> int:
    a: List[int] = [1, 2]
    b: List[int] = a
    b[0] = 9
    return a[0]


#@ ensures \result == 1
#@ assigns \nothing
def killed_alias() -> int:
    a: List[int] = [1]
    b: List[int] = []
    for i in range(2):
        b = a
        b = []
        b.append(i)
    return len(a)


#@ ensures \result == 2
#@ assigns \nothing
def read_only_alias() -> int:
    a: List[int] = [1, 2]
    b: List[int] = a
    return len(b)


if __name__ == "__main__":
    assert store_through_alias() == 9
    assert killed_alias() == 1
    assert read_only_alias() == 2
