"""1172 — ROUTE #71 POSITIVE CONTROL: the documented no-op boundary is untouched.

The repair refuses ONLY the `no_exception` claim over an erased operation. The identical
body WITHOUT a `no_exception` context must still emit and prove — the collection-parameter
no-op is a documented boundary with its own reopening capability, and route #71 is not the
place to change it. Without this control the fix would be indistinguishable from banning
the exemption outright.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass, field
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    s: Set[int] = field(default_factory=set)

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def probe(self, t: Set[int]) -> int:
        t.remove(5)
        return 0
