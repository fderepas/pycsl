r"""Test 1494 - ROUTE #150 (gen #29): the same `__post_init__` shape read through a method; `P(1).get() == 1` PROVED; CPython 7.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
_ = 0  # anchor


@dataclass
class P:
    x: int

    def __post_init__(self) -> None:
        self.x = 7

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P(1)
    return p.get()

