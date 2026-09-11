# pycsl-flags: --memory-model hoare
from dataclasses import dataclass
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires 1 not in t
    #@ ensures \result == 0
    #@ assigns \nothing
    def helper(self, s: Dict[int, int], t: Dict[int, int]) -> int:
        s[1] = 5
        if 1 in t:
            return 7
        return 0

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def caller2(self) -> int:
        u: Dict[int, int] = {}
        return self.helper(u, u)
