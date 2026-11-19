r"""Test 4683 -- gen #37 route #349 (expected FAIL): (new) `{D(1)}`; FAILED at base (Why3 type error), REFUSED now. REFUSED (PYCSL-R349-UNHASHABLE-RECORD, route #349).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g() -> int:
    s = {D(1)}
    return 1

if __name__ == "__main__":
    print(g())
