r"""Test 2294 — gen #36 r244 (expected FAIL): route #244, `remove` arm (same shape as 2293). CPython returns False; `\result == True`
PROVED at cdac19a6 and is now REFUSED.
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
        s.remove(1)

    #@ ensures \result == True
    #@ assigns \nothing
    def c(self) -> bool:
        s = set()
        s.add(1)
        self.m(s)
        return 1 in s


if __name__ == "__main__":
    assert C().c() is False
