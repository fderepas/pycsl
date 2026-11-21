r"""Test 4058 -- gen #37 route #315 (expected FAIL): dataclass `InitVar` handed to `__post_init__`, which stores `src[0]`; PROVED `xs[0] == 0` (CPython 1). REFUSED.
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

@dataclass
class D:
    n: int
    src: InitVar[List[int]]
    def __post_init__(self, src: List[int]) -> None:
        src[0] = src[0] + 1

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    d = D(1, xs)
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
