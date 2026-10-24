r"""Test 4674 -- gen #37 route #348 (expected FAIL): (new) `setattr(d, "x", 5)` on a frozen dataclass; REFUSED at base by the setattr no_exception rule, REFUSED now by #348 first. REFUSED (PYCSL-R348-IMMUTABLE-RECORD-STORE, route #348).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass(frozen=True)
class D:
    x: int

#@ no_exception \all
def f(d: D) -> int:
    setattr(d, "x", 5)
    return 5

if __name__ == "__main__":
    print(f(D(1)))
