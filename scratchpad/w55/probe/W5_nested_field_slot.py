# pycsl-flags: --memory-model hoare
from dataclasses import dataclass, field
from typing import List


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    m: List[List[int]] = field(default_factory=list)

    #@ requires True
    #@ ensures \result == 2
    #@ assigns self.m
    def probe(self) -> int:
        self.m = [[1], [2]]
        self.m[0] = self.m[1]
        self.m[0][0] = 9
        return self.m[1][0]
