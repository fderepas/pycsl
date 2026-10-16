r"""Test 2422 — gen #36 ch17 S-D (expected FAIL): set twin of 2420: `self.s.add(1); self.s.clear()` empties the set field (CPython 0), so
`\result == 1` is FALSE and must stay UNPROVED.
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

    #@ ensures \result == 1
    #@ assigns self.s
    def m(self) -> int:
        self.s.add(1)
        self.s.clear()
        return 1 if 1 in self.s else 0


if __name__ == "__main__":
    assert C().m() == 0
