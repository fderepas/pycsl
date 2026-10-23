r"""Test 2295 — gen #36 r244 (expected FAIL): route #244 from a MODULE-LEVEL caller (`c.m(s)` on a local instance; the same shape across
a file boundary is closed too, the imported method's body being in the unit). CPython returns
True; `\result == False` PROVED at cdac19a6 (cross-file spelling measured) and is now REFUSED.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    n: int = 0

    #@ assigns \nothing
    def m(self, s: Set[int]) -> None:
        s.add(1)


#@ ensures \result == False
#@ assigns \nothing
def f() -> bool:
    s: Set[int] = set()
    s.add(2)
    c = C()
    c.m(s)
    return 1 in s


if __name__ == "__main__":
    assert f() is True
