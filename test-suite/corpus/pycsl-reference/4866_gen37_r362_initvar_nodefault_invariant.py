r"""Test 4866 -- gen #37 route #362 (expected FAIL): witness r45: invariant dataclass with `k: InitVar[int]`; PROVED (CPython -1). REFUSED (PYCSL-R362-INITVAR-INVARIANT, route #362).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, InitVar

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    k: InitVar[int]

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    print(f(D(-1, 0)))
