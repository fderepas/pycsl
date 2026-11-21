r"""Test 2426 — gen #36 ch17 S-D (expected FAIL): STALE-ALIAS attempt through a PARAMETER: `link(p)` stores `p` into `self.d`; the caller
keeps `p`, calls `reset()` (`self.d.clear()`) and reads `p`. CPython: `p` is cleared (0), so
`\result == 1` is FALSE; the route #243 rule (E) must REFUSE the escaping argument.
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

    #@ assigns self.d
    def link(self, p: Dict[int, int]) -> None:
        self.d = p

    #@ assigns self.d
    def reset(self) -> None:
        self.d.clear()

    #@ ensures \result == 1
    #@ assigns self.d
    def m(self) -> int:
        p = {1: 5}
        self.link(p)
        self.reset()
        return 1 if 1 in p else 0


if __name__ == "__main__":
    assert C().m() == 0
