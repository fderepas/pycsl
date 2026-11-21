r"""Test 4684 -- gen #37 route #349 (expected FAIL): (new) `s: Set[D]` + `s.add(d)`; FAILED at base (Why3 type error), REFUSED now (annotation). REFUSED (PYCSL-R349-UNHASHABLE-RECORD, route #349).
"""
# pycsl-expected: FAIL
from typing import Set
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s: Set[D] = set()
    s.add(d)
    return 1

if __name__ == "__main__":
    print(g(D(1)))
