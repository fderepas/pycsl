r"""Test 4859 -- gen #37 route #360 (expected FAIL): (new) `@dataclass(slots=True)` with field x; a method stores `self.z`. REFUSED (PYCSL-R360-SLOTS-STORE, route #360).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass(slots=True)
class D:
    x: int
    def bump(self) -> None:
        self.z = 1

#@ no_exception \all
def f(d: D) -> int:
    d.bump()
    return d.x

if __name__ == "__main__":
    print(f(D(1)))
