r"""Test 4057 -- gen #37 route #315 (expected FAIL): user exception whose `__init__` calls `inc(a)` after `super().__init__`; PROVED `xs[0] == 0` (CPython 1). REFUSED.
"""
# pycsl-expected: FAIL
from typing import List, Dict
from dataclasses import dataclass, field, InitVar
from typing import NamedTuple

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

class E(Exception):
    def __init__(self, a: List[int]) -> None:
        super().__init__("e")
        self.v = inc(a)

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    try:
        raise E(xs)
    except E:
        pass
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
