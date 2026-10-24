r"""Test 4676 -- gen #37 route #348 (expected FAIL): (new) `self.x = 5` in a frozen dataclass method; FAILED at base (postcondition, not by design), REFUSED now. REFUSED (PYCSL-R348-IMMUTABLE-RECORD-STORE, route #348).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass(frozen=True)
class D:
    x: int
    #@ no_exception \all
    def bump(self) -> int:
        self.x = 5
        return 5

if __name__ == "__main__":
    print(D(1).bump())
