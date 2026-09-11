# pycsl-expected: FAIL
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
    #@ ensures \result == 1
    #@ assigns self.d
    def probe(self) -> int:
        p: Dict[int, int] = {1: 1}
        self.d = p
        p[1] = 2
        return self.d[1]
