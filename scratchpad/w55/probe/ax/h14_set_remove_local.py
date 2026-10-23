# pycsl-flags: --memory-model hoare
from dataclasses import dataclass
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ no_exception \all
    #@ ensures True
    #@ assigns \nothing
    def probe(self) -> int:
        u: Set[int] = {1}
        u.remove(5)
        return 0
