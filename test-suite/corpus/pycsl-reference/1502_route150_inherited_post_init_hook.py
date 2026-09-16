r"""Test 1502 - ROUTE #150 carrier-rerun on gen #29's own draft: a derived `@dataclass B(A)` has no `__post_init__`, but its synthesized constructor runs `A.__post_init__` (storing 7); `B(1).get() == 1` PROVED at HEAD AND on the first draft; CPython 7. The MRO is now searched for the hook.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
_ = 0  # anchor


@dataclass
class A:
    x: int

    def __post_init__(self) -> None:
        self.x = 7

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


@dataclass
class B(A):
    y: int = 0


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    b = B(1)
    return b.get()

