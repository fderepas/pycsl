r"""Test 3466 -- route #295 CONTROL (expected PASS): the dict/set partner rule stays out of the way of
faithful code — a READ-ONLY alias bound from a verified identity, a FRESH dict from a callee given no
dict, a scalar read through a method receiver (`d.get`) or a subscript, and a scalar-valued call over a
dict, each followed by a store through the ORIGINAL name, all prove as before.
"""
# pycsl-expected: PASS
from typing import Dict


#@ ensures \result == x
#@ assigns \nothing
def idd(x: Dict[int, int]) -> Dict[int, int]:
    return x


#@ assigns \nothing
def mk(k: int) -> Dict[int, int]:
    return {k: 1}


#@ ensures \result == 1
#@ assigns \nothing
def cnt(x: Dict[int, int]) -> int:
    return 1


#@ ensures \result == 1
def readonly_alias() -> int:
    d: Dict[int, int] = {1: 1}
    e = idd(d)
    return e[1]


#@ ensures \result == 2
def fresh_store() -> int:
    e = mk(1)
    e[1] = 2
    return e[1]


#@ ensures \result == 1
def get_then_store() -> int:
    d: Dict[int, int] = {1: 1}
    v = d.get(1, 0)
    d[1] = 2
    return v


#@ ensures \result == 1
def read_then_store() -> int:
    d: Dict[int, int] = {1: 1}
    n = d[1]
    d[1] = 5
    return n


#@ ensures \result == 2
def scalar_call_then_store() -> int:
    d: Dict[int, int] = {1: 1}
    n = cnt(d)
    d[1] = 2
    return n + d[1] - 1


if __name__ == "__main__":
    assert readonly_alias() == 1
    assert fresh_store() == 2
    assert get_then_store() == 1
    assert read_then_store() == 1
    assert scalar_call_then_store() == 2
