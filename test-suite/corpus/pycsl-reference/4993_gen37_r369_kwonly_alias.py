r"""Test 4993 -- gen #37 route #369 (expected FAIL): `_: KO` (`KW_ONLY as KO`) read as a field (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, KW_ONLY as KO

@dataclass
class D:
    x: int
    _: KO
    y: int = 0

#@ no_exception \all
def f(d: D) -> int:
    return d._

if __name__ == "__main__":
    print(f(D(1)))
