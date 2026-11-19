r"""Test 2420 — gen #36 ch17 S-D (expected FAIL): `self.d.clear()` on a dict RECORD field of a `@mutable_state` class is lowered as the
fresh-empty store `self.d <- (const None)`; after `self.d[1] = 5; self.d.clear()` the key is
gone (CPython returns 0), so `\result == 1` is FALSE and must stay UNPROVED (non-vacuity).
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

    #@ ensures \result == 1
    #@ assigns self.d
    def m(self) -> int:
        self.d[1] = 5
        self.d.clear()
        return 1 if 1 in self.d else 0


if __name__ == "__main__":
    assert C().m() == 0
