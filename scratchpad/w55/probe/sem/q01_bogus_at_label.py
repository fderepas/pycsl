# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    v: int = 0

    #@ requires self.v == 1
    #@ ensures \at(self.v, BOGUSLABEL) == 99
    #@ assigns self.v
    def probe(self) -> int:
        self.v = 2
        return 0
