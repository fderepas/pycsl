# pycsl-flags: --memory-model hoare
from dataclasses import dataclass
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires 1 not in s
    #@ ensures 1 not in s
    #@ assigns \nothing
    def m(self, s: Set[int]) -> None:
        s.add(1)
