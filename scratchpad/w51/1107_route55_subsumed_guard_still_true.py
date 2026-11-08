"""Test 1107 — ROUTE #55 PRECISION GUARD: the SUBSUMED shape keeps its faithful `true`.

TRUE OF THE PROGRAM: `o.probe({1: 5})` returns 7.

`if d and 1 in d:` — an EMPTY `d` makes `1 in d` False anyway, so the short-circuit changes
nothing and answering `true` for the left conjunct is EXACT, not an over-approximation. The
27th plane's justification ("the `in` that follows does the real check") is right about THIS
shape; route #55 is that the arm also fired OUTSIDE it, on the bare guard (1104-1106).

This file is why the repair is a NARROWING and not a retreat, and it is negative-tested both
ways: it PROVES with the subsumption exemption and FAILS without it. It is also what keeps
the build byte-inert — the one live site in the 53-file mirror
(`module6_whyml/expressions.py`: `if subst and name in subst:`) has exactly this shape, so
zero mirror emissions move and no re-proof is owed.
"""
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
