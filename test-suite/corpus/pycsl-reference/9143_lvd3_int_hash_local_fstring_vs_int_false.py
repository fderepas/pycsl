r"""Test 9143 -- lvD3 control (expected FAIL, also FAIL under C2): the KEPT position. `f"*{name}"`
renders the hash through the program `val int_to_string` (no `function`: each call is a fresh unrelated
string), so it cannot be equated with `f"*{x}"` even when `x` equals the hash. CPython: "*abc" != "*1824800645".
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ requires x == 1824800645
#@ ensures \result == True
#@ assigns \nothing
def f(x: int) -> bool:
    name = x
    name = "abc"
    return f"*{name}" == f"*{x}"


if __name__ == "__main__":
    r = f(1824800645)
    print("VIOLATION contract" if r is not True else "result", r)
