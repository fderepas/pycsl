r"""Test 2304 — gen #36 r243 (expected FAIL): route #243: `link(p)` states `self.d == p` (true at return); the caller then stores through
its local `p`. CPython returns True; `\result == False` PROVED at cdac19a6, now REFUSED.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    d: Dict[int, int] = field(default_factory=dict)

    #@ ensures self.d == p
    #@ assigns self.d
    def link(self, p: Dict[int, int]) -> None:
        self.d = p

    #@ ensures \result == False
    #@ assigns self.d
    def m(self) -> bool:
        p: Dict[int, int] = {}
        self.link(p)
        p[1] = 5
        return 1 in self.d


if __name__ == "__main__":
    assert C().m() is True
