# pycsl-flags: --memory-model hoare
from dataclasses import dataclass, field
from typing import List


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    l: List[int] = field(default_factory=list)

    #@ requires True
    #@ ensures \result == 1
    #@ assigns self.l
    def probe(self) -> int:
        p: List[int] = [1]
        self.l = p
        p[0] = 2
        return self.l[0]
