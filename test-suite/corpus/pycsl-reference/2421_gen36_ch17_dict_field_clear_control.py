r"""Test 2421 — gen #36 ch17 S-D (expected PASS): CONTROL for 2420: the same body with the TRUE claim `\result == 0` proves (CPython 0).
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

    #@ ensures \result == 0
    #@ assigns self.d
    def m(self) -> int:
        self.d[1] = 5
        self.d.clear()
        return 1 if 1 in self.d else 0


if __name__ == "__main__":
    assert C().m() == 0
