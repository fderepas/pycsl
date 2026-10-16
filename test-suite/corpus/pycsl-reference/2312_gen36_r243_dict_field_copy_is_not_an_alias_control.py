r"""Test 2312 — gen #36 r243 (expected PASS): route #243 CONTROL. `self.g = dict(self.d)` is a
COPY in Python too, so it creates no second name: in a unit that DOES mutate a dict field in
place (`self.d[1] = 5`), the FRESH field store is not refused and the method keeps proving
(CPython: True). (`1 in self.g` after the store is not decided either way: the copy's contents
are not modelled, before or after the repair.)
"""
# pycsl-expected: PASS
from dataclasses import dataclass, field
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    d: Dict[int, int] = field(default_factory=dict)
    g: Dict[int, int] = field(default_factory=dict)

    #@ ensures \result == True
    #@ assigns self.d, self.g
    def m(self) -> bool:
        self.g = dict(self.d)
        self.d[1] = 5
        return 1 in self.d


if __name__ == "__main__":
    assert C().m() is True
