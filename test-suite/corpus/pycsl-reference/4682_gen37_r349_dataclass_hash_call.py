r"""Test 4682 -- gen #37 route #349 (expected FAIL): (new) `hash(d)` of an eq-dataclass; FAILED at base (Why3 type error), REFUSED now. REFUSED (PYCSL-R349-UNHASHABLE-RECORD, route #349).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    h = hash(d)
    return 1

if __name__ == "__main__":
    print(g(D(1)))
