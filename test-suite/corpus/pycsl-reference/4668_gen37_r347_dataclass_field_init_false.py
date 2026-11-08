r"""Test 4668 -- gen #37 route #347 (expected FAIL): (new) `x: int = field(init=False)` without default; PROVED (CPython AttributeError). REFUSED (PYCSL-R347-FIELD-MAYBE-UNASSIGNED, route #347).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field

@dataclass
class D:
    n: int
    x: int = field(init=False)

#@ no_exception \all
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    print(f(D(1)))
