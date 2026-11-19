# pycsl-flags: --memory-model hoare
from dataclasses import dataclass
from typing import Set




@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def helper(self, s: Set[int]) -> None:
        s.add(1)

    #@ requires 1 not in s
    #@ ensures 1 not in s
    #@ assigns \nothing
    def caller(self, s: Set[int]) -> None:
        self.helper(s)
