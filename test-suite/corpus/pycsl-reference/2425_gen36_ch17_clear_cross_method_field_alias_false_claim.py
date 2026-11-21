r"""Test 2425 — gen #36 ch17 S-D (expected FAIL): STALE-ALIAS attempt, CROSS-METHOD: `link()` does `self.g = self.d`; `m()` stores through
`self.g`, clears `self.d` and reads `self.g`. CPython (after `link`): one dict, cleared (0).
`\result == 1` is FALSE; the route #243 unit-wide rule (F) must REFUSE the field alias.
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
    g: Dict[int, int] = field(default_factory=dict)

    #@ assigns self.g
    def link(self) -> None:
        self.g = self.d

    #@ ensures \result == 1
    #@ assigns self.d, self.g
    def m(self) -> int:
        self.g[1] = 5
        self.d.clear()
        return 1 if 1 in self.g else 0


if __name__ == "__main__":
    c = C()
    c.link()
    assert c.m() == 0
