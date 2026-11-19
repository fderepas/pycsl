r"""Test 3640 -- gen #37 route #302 (expected PASS): CONTROLS -- a target RE-BOUND after its loop before the read (`x = "a"` kills the staleness: no write-back, byte-identical), a FAITHFUL write-back proved through a loop invariant on the outer name, two sequential loops on the same name each read only inside, and a read of the name BEFORE its loop. All honest; must still PROVE.
"""
# pycsl-expected: PASS
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(e) == 1
#@ ensures \result == "a"
#@ assigns \nothing
def rebind_after(e: List[str]) -> str:
    x = ""
    for x in e:
        pass
    x = "a"
    return x

#@ requires len(e) == 1
#@ ensures \result == "" or \result == e[0]
#@ assigns \nothing
def faithful_write_back(e: List[str]) -> str:
    x = ""
    #@ loop invariant x == "" or x == e[0]
    for x in e:
        pass
    return x

#@ ensures \result >= 0
#@ assigns \nothing
def sequential_loops(a: List[int], b: List[int]) -> int:
    t = 0
    #@ loop invariant t >= 0
    for x in a:
        t = t + 1
    #@ loop invariant t >= 0
    for x in b:
        t = t + 1
    return t

#@ ensures \result == y
#@ assigns \nothing
def read_before(e: List[int], y: int) -> int:
    x = y
    r = x
    for x in e:
        pass
    return r

if __name__ == "__main__":
    assert rebind_after(["q"]) == "a"
    assert faithful_write_back(["q"]) == "q"
    assert sequential_loops([1], [2, 3]) == 3
    assert read_before([5], 9) == 9
