r"""Test 2314 — gen #36 r244 (expected PASS): route #244 CONTROL: a caller handing the mutating method a FRESH, single-use set is not
refused (no second name can observe it). CPython: 7.
"""
# pycsl-expected: PASS
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

    #@ ensures \result == 7
    #@ assigns \nothing
    def c(self) -> int:
        s: Set[int] = set()
        self.m(s)
        return 7


if __name__ == "__main__":
    assert C().c() == 7
