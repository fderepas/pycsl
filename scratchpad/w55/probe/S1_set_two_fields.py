# pycsl-flags: --memory-model hoare
from dataclasses import dataclass, field
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    s: Set[int] = field(default_factory=set)
    t: Set[int] = field(default_factory=set)

    #@ requires True
    #@ ensures \result == 1
    #@ assigns self.s, self.t
    def probe(self) -> int:
        p: Set[int] = {1}
        self.s = p
        self.t = p
        self.s.add(2)
        return len(self.t)
