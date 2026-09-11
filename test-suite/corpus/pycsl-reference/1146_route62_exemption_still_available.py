"""1146 — ROUTE #62 POSITIVE CONTROL: the @mutable_state exemption still works.

The exemption exists because the mirror's reflecting handlers really do mutate sibling
collection arguments, and NONE of them names one in a contract. Removing the exemption
outright breaks three mirror files. This driver is that legitimate shape — a set formal
mutated in a @mutable_state class with no contract naming it, and no contract-named
collection passed to a call — and it must keep emitting. Without this control, a repair
that simply refused every collection-param mutation would satisfy 1145 and silently take
the mirror with it.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures \result == 7
    #@ assigns \nothing
    def m(self, s: Set[int]) -> int:
        s.add(1)
        return 7
