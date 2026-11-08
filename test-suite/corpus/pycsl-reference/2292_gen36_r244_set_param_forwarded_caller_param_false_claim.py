r"""Test 2292 — gen #36 r244 (expected FAIL): route #244 through a FORWARDED parameter: `c(self, s)` passes its own parameter to the
mutating `m` and then reads it. CPython returns True; `\result == False` PROVED at cdac19a6
and is now REFUSED (`s` is used again after the call).
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
    def c(self, s: Set[int]) -> bool:
        if 1 in s:
            return False
        self.m(s)
        return 1 in s


if __name__ == "__main__":
    assert C().c(set()) is True
