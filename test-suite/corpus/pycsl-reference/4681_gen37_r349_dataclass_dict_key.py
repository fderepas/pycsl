r"""Test 4681 -- gen #37 route #349 (expected FAIL): (new) eq-dataclass as a dict key; FAILED at base (Why3 type error), REFUSED now. REFUSED (PYCSL-R349-UNHASHABLE-RECORD, route #349).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    m = {d: 1}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
