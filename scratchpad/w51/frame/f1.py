# pycsl-flags: --memory-model hoare
# FRAME PROBE 1 — the named follow-up of the 27th plane: a self-field write on the branch
# the always-present model DELETES is invisible to the `assigns` proof.
# `if <dict param>:` is modelled `true`, so the ELSE branch is deleted. Python with an
# EMPTY dict takes it and writes self.tag.
from dataclasses import dataclass
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def probe(self, d: Dict[int, int]) -> int:
        if d:
            if 1 in d:
                return 0
            return 0
        self.tag = 7
        return 0


if __name__ == "__main__":
    o = C()
    assert o.probe({}) == 0
    assert o.tag == 7
