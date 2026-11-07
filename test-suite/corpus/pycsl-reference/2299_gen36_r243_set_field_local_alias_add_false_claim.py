r"""Test 2299 — gen #36 r243 (expected FAIL): route #243 witness `field_set_alias_local`: `a = self.s` then `self.s.add(1)`; route #59's
local-alias guard saw only STORES, not mutator calls. CPython returns True; PROVED at
cdac19a6, now REFUSED by the extended route #59 guard.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    s: Set[int] = field(default_factory=set)

    #@ ensures \result == False
    #@ assigns self.s
    def m(self) -> bool:
        if 1 in self.s:
            return False
        a = self.s
        self.s.add(1)
        return 1 in a


if __name__ == "__main__":
    assert C().m() is True
