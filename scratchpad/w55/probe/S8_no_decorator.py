# pycsl-flags: --memory-model hoare
from dataclasses import dataclass
from typing import Set


@dataclass
class C:
    tag: int = 0

    #@ requires 1 not in t
    #@ ensures \result == 0
    #@ assigns \nothing
    def helper(self, s: Set[int], t: Set[int]) -> int:
        s.add(1)
        if 1 in t:
            return 7
        return 0

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def caller2(self) -> int:
        u: Set[int] = set()
        return self.helper(u, u)
