r"""Test 1722 — ROUTE #212: `--verify-imports` refuses a dependency that does not verify.

Route #212 is the wide hole: an importing unit BELIEVES every contract of an imported
module — frames, postconditions, class invariants — and nothing checks the module was ever
verified. Demonstrated with two ordinary files and no annotation tricks:
`multi_file_lib/r212_unverified.py` declares `#@ assigns \nothing` over a body that writes
`a[0]`, FAILS compiled alone, and an importer of it PROVED `x - a[0] == 0` where CPython
answers -4.

The route itself stays OPEN (the general repair is a module-level certificate, because
re-emitting the obligation the way route #205 did needs the BODIES the import boundary
deliberately does not lower). `--verify-imports` is that certificate, made available and
OFF BY DEFAULT so no existing run changes: it verifies each resolved local import
transitively, with a seen-set so cycles terminate.

This file must FAIL: the flag is on and the dependency does not verify. Control: 1723.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare --verify-imports
from typing import List

from multi_file_lib.r212_unverified import touch

_ = 0  # anchor


#@ requires \length(a) >= 1
#@ ensures \result == 0
def caller(a: List[int]) -> int:
    x = a[0]
    touch(a)
    return x - a[0]
