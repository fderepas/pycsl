r"""Test 5007 -- gen #37 route #369 (expected FAIL): required `field(kw_only=True)` missing in `D(5)` (never arity-checked) (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field

@dataclass
class D:
    x: int = field(kw_only=True)
    y: int = 0

#@ no_exception \all
def f() -> int:
    d = D(5)
    return d.y

if __name__ == "__main__":
    print(f())
