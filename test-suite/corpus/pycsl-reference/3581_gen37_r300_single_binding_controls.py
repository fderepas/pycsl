r"""Test 3581 -- gen #37 route #300 (expected PASS): CONTROLS: a name with exactly ONE static binding to a literal keeps its fold (len / index / dict len / str len).
"""
# pycsl-expected: PASS
from typing import Any, List, Dict, Set, Tuple, Optional
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def dict_len() -> int:
    d = {"a": 1}
    return len(d)

#@ ensures \result == 6
#@ assigns \nothing
def tuple_idx() -> int:
    t = (5, 6)
    return t[1]

#@ requires c != 1
#@ ensures \result == 3
#@ assigns \nothing
def list_len(c: int) -> int:
    xs = [1, 2, 3]
    if c == 1:
        return 0
    return len(xs)

#@ requires c != 1
#@ ensures \result == 2
#@ assigns \nothing
def str_len(c: int) -> int:
    s = "ab"
    return len(s)

if __name__ == "__main__":
    assert dict_len() == 1
    assert tuple_idx() == 6
    assert list_len(0) == 3
    assert str_len(0) == 2
