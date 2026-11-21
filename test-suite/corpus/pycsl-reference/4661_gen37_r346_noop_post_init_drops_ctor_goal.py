r"""Test 4661 -- gen #37 route #346 (expected FAIL): (new) a no-op `__post_init__` makes the construction opaque and drops the constructor-invariant goal; FAILED at base (call-site precondition), REFUSED now. REFUSED (PYCSL-R346-POST-INIT-INVARIANT, route #346).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    def __post_init__(self) -> None:
        pass

#@ ensures \result >= 0
def g() -> int:
    d = D(-5)
    return d.x

if __name__ == "__main__":
    assert g() >= 0
