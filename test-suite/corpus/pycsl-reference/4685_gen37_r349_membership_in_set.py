r"""Test 4685 -- gen #37 route #349 (expected FAIL): (new) `d in {D(2)}`; FAILED at base (Why3 type error), REFUSED now. REFUSED (PYCSL-R349-UNHASHABLE-RECORD, route #349).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    b = d in {D(2)}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
