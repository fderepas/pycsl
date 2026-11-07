# pycsl-flags: --memory-model hoare
from dataclasses import dataclass, field
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    d: Dict[int, int] = field(default_factory=dict)

    #@ requires True
    #@ ensures \result == 2
    #@ assigns self.d
    def probe(self) -> int:
        p: Dict[int, int] = {}
        self.d = p
        self.d[1] = 2
        return self.d[1]
