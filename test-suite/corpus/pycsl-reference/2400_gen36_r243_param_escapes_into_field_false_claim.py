r"""Test 2300 — gen #36 r243 (expected FAIL): route #243, escape through a call: `link(p)` stores its parameter into `self.d`; the caller
keeps `p`, stores through the field, and reads `p`. CPython returns True; PROVED at cdac19a6,
now REFUSED at the call (`p` is used again afterwards).
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

    #@ ensures \result == False
    #@ assigns self.d
    def m(self) -> bool:
        p: Dict[int, int] = {}
        self.link(p)
        self.d[1] = 5
        return 1 in p


if __name__ == "__main__":
    assert C().m() is True
