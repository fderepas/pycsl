r"""Test 9000 -- lvF cap-trusted-val-unit-return (expected PASS): a `\trusted` stub with a `pass`
placeholder body declared `-> Any` / `-> Dict[str, int]` / `-> List[int]` is a `val` that RETURNS a
value of the declared model type (`int` / `map int (option int)` / `array int`), not `unit`. At base
each `val` announced `: unit`, so a caller that binds the result (`a = lookup(k)`) did not type-check
(`This expression has type (), but is expected to have type int`). Nothing is claimed about the
returned value (no ensures is added): the caller proves only facts independent of it.
Twins: 9001 / 9002 / 9003 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import Any, Dict, List


#@ \trusted reviewer: lvF
#@ assigns \nothing
def lookup(k: int) -> Any:
    pass


#@ \trusted reviewer: lvF
#@ assigns \nothing
def table(k: int) -> Dict[str, int]:
    pass


#@ \trusted reviewer: lvF
#@ assigns \nothing
def items(k: int) -> List[int]:
    pass


#@ ensures \result == k + 1
#@ assigns \nothing
def bump(k: int) -> int:
    a = lookup(k)
    d = table(k)
    xs = items(k)
    return k + 1


if __name__ == "__main__":
    r = bump(4)
    print("VIOLATION contract" if r != 5 else "result", r)
