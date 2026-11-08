"""Test 1195 — ROUTE #77, THE `len()` CARRIER: `del <seq>[i:j]` then `len(...)`.

The second of route #77's three proving carriers (see 1194 for the full route). The erased
slice delete leaves the modelled sequence at its ORIGINAL length, so a claim about `len`
after the delete is decided against a sequence the run demonstrably does not have.
Measured, before the refusal:

    xs: List[int] = [1, 2, 3]
    del xs[0:2]
    return len(xs)
    #@ ensures \\result == 3             <-- FALSE OF THE PROGRAM (Python returns 1)

    [+] Verification SUCCESS! All contracts formally proven.

And the TRUE twin (`#@ ensures \\result == 1`) was REFUSED — the emitter did not merely
fail to know the answer, it proved the wrong one and refused the right one.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires True
#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2, 3]
    del xs[0:2]
    return len(xs)
