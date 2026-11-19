r"""Test 2423 — gen #36 ch17 S-D (expected PASS): CONTROL for 2422: the TRUE claim `\result == 0` proves (CPython 0).
"""
# pycsl-expected: PASS
from dataclasses import dataclass, field
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    s: Set[int] = field(default_factory=set)

    #@ ensures \result == 0
    #@ assigns self.s
    def m(self) -> int:
        self.s.add(1)
        self.s.clear()
        return 1 if 1 in self.s else 0


if __name__ == "__main__":
    assert C().m() == 0
