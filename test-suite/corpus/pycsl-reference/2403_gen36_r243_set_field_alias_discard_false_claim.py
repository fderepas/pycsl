r"""Test 2303 — gen #36 r243 (expected FAIL): route #243, `discard` through the other field: after `link()`, `self.s.discard(1)` empties
`self.t` too. CPython returns False, so `\result == True` is FALSE; PROVED at cdac19a6, now
REFUSED.
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
    t: Set[int] = field(default_factory=set)

    #@ assigns self.t
    def link(self) -> None:
        self.t = self.s

    #@ ensures \result == True
    #@ assigns self.s
    def m(self) -> bool:
        if 1 not in self.t:
            return True
        self.s.discard(1)
        return 1 in self.t


if __name__ == "__main__":
    c = C()
    c.s.add(1)
    c.link()
    assert c.m() is False
