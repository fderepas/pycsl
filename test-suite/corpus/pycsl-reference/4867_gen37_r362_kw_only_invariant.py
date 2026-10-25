r"""Test 4867 -- gen #37 route #362 (expected FAIL): (new) invariant dataclass with a `_: KW_ONLY` sentinel; the goal is dropped the same way; PROVED (CPython -1). REFUSED (PYCSL-R362-INITVAR-INVARIANT, route #362).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, KW_ONLY

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    _: KW_ONLY
    y: int = 0

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    print(f(D(-1)))
