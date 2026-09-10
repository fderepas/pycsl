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
        self.d[1] = 1
        b: Dict[int, int] = self.d
        b[1] = 2
        return self.d[1]
