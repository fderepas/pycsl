r"""Test 4679 -- gen #37 route #349 (expected FAIL): witness e09: eq-dataclass `{d}`; PROVED (CPython TypeError). REFUSED (PYCSL-R349-UNHASHABLE-RECORD, route #349).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
