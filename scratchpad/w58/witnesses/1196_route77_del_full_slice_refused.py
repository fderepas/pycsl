"""Test 1196 — ROUTE #77, THE FULL-SLICE CARRIER: `del xs[:]` (the idiomatic list clear).

The third of route #77's three proving carriers (see 1194 for the full route). `del xs[:]`
is the standard Python idiom for emptying a list in place, so this is the carrier a real
program is most likely to contain. It was erased identically. Measured, before the refusal:

    xs: List[int] = [1, 2, 3]
    del xs[:]
    return len(xs)
    #@ ensures \\result == 3             <-- FALSE OF THE PROGRAM (Python returns 0)

    [+] Verification SUCCESS! All contracts formally proven.

A DYNAMIC bound was also measured and erased identically (`del xs[0:n]`), which establishes
that the defect is the ERASURE itself and not an artefact of folding constant bounds.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires True
#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2, 3]
    del xs[:]
    return len(xs)
