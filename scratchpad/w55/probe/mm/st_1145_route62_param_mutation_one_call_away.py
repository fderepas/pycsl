"""1145 — ROUTE #62 NEGATIVE: the @mutable_state collection-param no-op, one call away.

`helper` mutates the set and its own contract names nothing, so the direct guard never
fires; `caller` names the parameter it passed in, and its `ensures` PROVED while CPython
answers False. The identical program without @mutable_state is refused outright, so the
decorator is what converted a hard refusal into a silent no-op.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model store
from dataclasses import dataclass
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def helper(self, s: Set[int]) -> None:
        s.add(1)

    #@ requires 1 not in s
    #@ ensures 1 not in s
    #@ assigns \nothing
    def caller(self, s: Set[int]) -> None:
        self.helper(s)
