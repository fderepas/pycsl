# pycsl-flags: --memory-model hoare
from dataclasses import dataclass
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def helper(self, d: Dict[int, int]) -> None:
        d[1] = 99

    #@ requires d[1] == 1
    #@ ensures d[1] == 1
    #@ assigns \nothing
    def caller(self, d: Dict[int, int]) -> None:
        self.helper(d)
