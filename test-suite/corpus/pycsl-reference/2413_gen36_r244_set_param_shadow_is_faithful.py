r"""Test 2313 — gen #36 r244 (expected PASS): route #244 CONTROL (the repair is faithful, not only refusing): the shadowed set parameter
sees its own `add`, so `\result == True` PROVES (CPython: True). At cdac19a6 the add was
erased and this true claim could not be proved.
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

    #@ ensures \result == True
    #@ assigns \nothing
    def m(self, s: Set[int]) -> bool:
        s.add(1)
        return 1 in s


if __name__ == "__main__":
    assert C().m(set()) is True
