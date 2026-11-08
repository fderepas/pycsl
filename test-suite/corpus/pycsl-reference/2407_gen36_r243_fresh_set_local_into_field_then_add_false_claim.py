r"""Test 2307 — gen #36 r243 (expected FAIL): route #243 / route #59 carrier 6 for a SET: `a = set(); self.s = a; self.s.add(1)`, read
`a`. Route #59's carrier only tracked dict LITERAL locals and STORES. CPython returns True;
PROVED at cdac19a6, now REFUSED (`a` is used again after the field store).
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

    #@ ensures \result == False
    #@ assigns self.s
    def m(self) -> bool:
        a: Set[int] = set()
        self.s = a
        self.s.add(1)
        return 1 in a


if __name__ == "__main__":
    assert C().m() is True
