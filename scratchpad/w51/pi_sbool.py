# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures \result == 7
    #@ assigns \nothing
    def probe(self, s: bool) -> int:
        if s is None:
            return 0
        return 7
