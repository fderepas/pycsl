r"""Test 2298 — gen #36 r243 (expected FAIL): route #243 witness `field_alias3`: the set twin of 2297 (`self.t = self.s`, then
`self.s.add(1)`). CPython returns True; PROVED at cdac19a6, now REFUSED.
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

    #@ ensures \result == False
    #@ assigns self.s
    def m(self) -> bool:
        if 1 in self.t:
            return False
        self.s.add(1)
        return 1 in self.t


if __name__ == "__main__":
    c = C()
    c.link()
    assert c.m() is True
