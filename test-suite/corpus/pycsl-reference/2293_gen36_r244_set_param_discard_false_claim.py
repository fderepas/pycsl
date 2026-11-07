r"""Test 2293 — gen #36 r244 (expected FAIL): route #244, `discard` arm: the callee removes 1 from the caller's set. CPython returns False,
so `\result == True` is FALSE; it PROVED at cdac19a6 and is now REFUSED.
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
        s.discard(1)

    #@ ensures \result == True
    #@ assigns \nothing
    def c(self) -> bool:
        s = set()
        s.add(1)
        self.m(s)
        return 1 in s


if __name__ == "__main__":
    assert C().c() is False
