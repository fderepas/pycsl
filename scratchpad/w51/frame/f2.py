# pycsl-flags: --memory-model hoare
# FRAME PROBE 2 — the ENSURES half at the same arm. `if <dict param>:` is `true`, so the
# else branch is deleted; the postcondition is then proved over a strict subset.
from dataclasses import dataclass
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures \result == 7
    #@ assigns \nothing
    def probe(self, d: Dict[int, int]) -> int:
        if d:
            if 1 in d:
                return 7
            return 7
        return 0


if __name__ == "__main__":
    o = C()
    assert o.probe({}) == 0
