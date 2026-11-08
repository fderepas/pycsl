# pycsl-flags: --memory-model hoare
from dataclasses import dataclass, field
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    s: Set[int] = field(default_factory=set)

    #@ requires True
    #@ no_exception \all
    #@ ensures True
    #@ assigns \nothing
    def probe(self, t: Set[int]) -> int:
        t.remove(5)
        return 0
