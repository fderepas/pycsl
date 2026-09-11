# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    v: int = 1

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def g(self) -> int:
        self.v = 9
        return 0

    #@ requires self.v == 1
    #@ ensures \result == 1
    #@ assigns \nothing
    def f(self) -> int:
        self.g()
        return self.v
