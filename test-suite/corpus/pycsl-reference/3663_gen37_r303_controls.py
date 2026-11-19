r"""Test 3663 -- gen #37 route #303 (expected PASS): CONTROLS -- the unpacking/rebind shapes route #303 keeps: a pure PERMUTATION swap of two dicts then a store (`g, h = h, g`: no new sharing), a READ-ONLY tuple alias of a dict, an int tuple update (`a, b = b, a + b`), a FRESH dict literal in a tuple slot then a store, a read-only REBIND `h = g` of a declared dict, and a read-only dict rebind inside a loop. All honest; must still PROVE.
"""
from typing import Dict


#@ ensures \result == 5
#@ assigns \nothing
def perm_swap(n: int) -> int:
    g: Dict[str, int] = {"G": 0}
    h: Dict[str, int] = {"G": 1}
    g, h = h, g
    h["G"] = 5
    return h["G"]


#@ ensures \result == 7
#@ assigns \nothing
def readonly_alias(n: int) -> int:
    g: Dict[str, int] = {"G": 7}
    h: Dict[str, int] = {"G": 0}
    h, k = g, 1
    return h["G"]


#@ ensures \result == 5
#@ assigns \nothing
def int_tuple(n: int) -> int:
    a = 2
    b = 3
    a, b = b, a + b
    return b


#@ ensures \result == 5
#@ assigns \nothing
def fresh_slot(n: int) -> int:
    h: Dict[str, int] = {"G": 0}
    h, k = {"G": 1}, 1
    h["G"] = 5
    return h["G"]


#@ ensures \result == 7
#@ assigns \nothing
def readonly_rebind(n: int) -> int:
    g: Dict[str, int] = {"G": 7}
    h: Dict[str, int] = {"G": 0}
    h = g
    return h["G"]


#@ ensures \result == 7
#@ assigns \nothing
def loop_readonly(n: int) -> int:
    g: Dict[str, int] = {"G": 7}
    h: Dict[str, int] = {"G": 0}
    i = 0
    #@ loop invariant 0 <= i <= 2
    #@ loop invariant g["G"] == 7
    #@ loop variant 2 - i
    while i < 2:
        h = g
        i = i + 1
    return g["G"]


if __name__ == "__main__":
    assert perm_swap(0) == 5
    assert readonly_alias(0) == 7
    assert int_tuple(0) == 5
    assert fresh_slot(0) == 5
    assert readonly_rebind(0) == 7
    assert loop_readonly(0) == 7
