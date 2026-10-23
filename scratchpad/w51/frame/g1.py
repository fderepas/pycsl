# pycsl-flags: --memory-model hoare
# ROUTE #55 PRECISION GUARD: the SUBSUMED shape must keep its faithful `true`.
# `if d and 1 in d:` — an empty `d` makes `1 in d` False anyway, so the short-circuit
# changes nothing and `true` for the left conjunct is EXACT. The precondition supplies
# the membership, so this PROVES under the subsumption exemption and would FAIL if the
# left conjunct were made opaque.
from dataclasses import dataclass
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires \has_key(d, 1)
    #@ ensures \result == 7
    #@ assigns \nothing
    def probe(self, d: Dict[int, int]) -> int:
        if d and 1 in d:
            return 7
        return 0


if __name__ == "__main__":
    o = C()
    assert o.probe({1: 5}) == 7
