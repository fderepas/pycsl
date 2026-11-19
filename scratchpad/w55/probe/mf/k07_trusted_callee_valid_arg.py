# pycsl-flags: --memory-model hoare
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class C:
    tag: int = 0

    #@ \trusted reviewer: probe
    #@ requires x > 0
    #@ ensures \result > 0
    #@ assigns \nothing
    def pos_only(self, x: int) -> int:
        return x

    #@ requires True
    #@ ensures \result > 0
    #@ assigns \nothing
    def caller(self) -> int:
        return self.pos_only(5)
