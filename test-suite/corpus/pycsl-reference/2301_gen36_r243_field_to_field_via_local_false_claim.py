r"""Test 2301 — gen #36 r243 (expected FAIL): route #243: the field alias routed through a local (`a = self.d; self.g = a`). CPython
returns True; PROVED at cdac19a6, now REFUSED.
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
        a = self.d
        self.g = a

    #@ ensures \result == False
    #@ assigns self.d
    def m(self) -> bool:
        if 1 in self.g:
            return False
        self.d[1] = 5
        return 1 in self.g


if __name__ == "__main__":
    c = C()
    c.link()
    assert c.m() is True
