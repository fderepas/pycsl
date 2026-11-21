r"""Test 3621 -- gen #37 route #301 (expected PASS): CONTROLS -- the target shapes route #301 keeps: a flat tuple of names (`u, t = x, x + 1`), a flat tuple for-target (`for u, v in ps`), a chained name assignment (`t = s = ...`), two loops re-binding the same flat tuple components (`for k, v in a.items()` twice). All honest; must still PROVE.
"""
from typing import Any, List, Dict, Set, Tuple, Optional

#@ ensures \result == x + 1
#@ assigns \nothing
def flat_tuple(x: int) -> int:
    t = 0
    u, t = x, x + 1
    return t

#@ ensures \result >= 0
#@ assigns \nothing
def for_flat(ps: List[Tuple[int, int]]) -> int:
    k = 0
    #@ loop invariant k >= 0
    for u, v in ps:
        k = k + 1
    return k

#@ requires len(e) == 2
#@ ensures \result == e[0]
#@ assigns \nothing
def chained(e: List[int]) -> int:
    t = 0
    s = 0
    t = s = e[0]
    return s

#@ ensures \result >= 0
#@ assigns \nothing
def two_loops(a: Dict[str, int], b: Dict[str, int]) -> int:
    n = 0
    #@ loop invariant n >= 0
    for k, v in a.items():
        n = n + 1
    #@ loop invariant n >= 0
    for k, v in b.items():
        if k == "x":
            n = n + 1
    return n

if __name__ == "__main__":
    assert flat_tuple(3) == 4
    assert for_flat([(1, 2), (3, 4)]) == 2
    assert chained([8, 9]) == 8
    assert two_loops({"a": 1}, {"x": 2}) == 2
