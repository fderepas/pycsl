r"""Test 1509 - ROUTE #151 x #144 (gen #29): a BASE `field(init=False, default=5)` merged into a derived `@dataclass B(A)`; `B(3).gety() == 3` PROVED; CPython 5.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
_ = 0  # anchor


@dataclass
class A:
    y: int = field(init=False, default=5)

    #@ requires True
    #@ ensures \result == self.y
    def gety(self) -> int:
        return self.y


@dataclass
class B(A):
    x: int = 0


#@ ensures \result == 3
#@ assigns \nothing
def probe() -> int:
    b = B(3)
    return b.gety()

