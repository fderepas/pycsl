r"""Test 2297 — gen #36 r243 (expected FAIL): route #243 witness `field_alias2`, CROSS-METHOD: `link()` aliases `self.g = self.d`; `m()`
stores through `self.d` and reads `self.g`, with no precondition. CPython (after `link()`)
returns True; `\result == False` PROVED at cdac19a6 and `link` is now REFUSED.
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
