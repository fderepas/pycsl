# pycsl-flags: --memory-model hoare
from dataclasses import dataclass, field
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    d: Dict[int, int] = field(default_factory=dict)
    e: Dict[int, int] = field(default_factory=dict)

    #@ requires True
    #@ ensures \result == 1
    #@ assigns self.d, self.e
    def probe(self) -> int:
        self.d = {1: 1}
        self.e = self.d
        self.d[1] = 2
        return self.e[1]
