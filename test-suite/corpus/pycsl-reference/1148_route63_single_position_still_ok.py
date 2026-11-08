"""1148 — ROUTE #63 POSITIVE CONTROL: a single-occurrence call is untouched.

The route #63 guard refuses only the SAME dict/set in two or more argument positions of one
call. Passing a set to a callee ONCE is the ordinary shape the mirror's reflecting handlers
use everywhere, and it must keep working — otherwise the repair has over-reached from an
aliasing barrier into a ban on passing collections at all.
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
    #@ ensures \result == 0
    #@ assigns \nothing
    def helper(self, s: Set[int], n: int) -> int:
        if n in s:
            return 0
        return 0

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def caller2(self) -> int:
        u: Set[int] = set()
        return self.helper(u, 3)
