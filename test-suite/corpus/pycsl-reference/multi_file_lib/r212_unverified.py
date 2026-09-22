"""(#49) gen #30, route #212 — an INTENTIONALLY UNVERIFIABLE dependency.

`touch` declares `#@ assigns \\nothing` over a body that writes `a[0]`. Compiled on its
own this module FAILS, and that is the POINT: it is the dependency that witness 1722 imports
under `--verify-imports` (which must refuse) and that witness 1723's honest twin replaces.

DO NOT "FIX" THIS FILE. Any sweep that verifies the corpus's locally-imported modules must
baseline it by name as an intentional negative.
"""
from typing import List

_ = 0  # anchor


#@ requires \length(a) >= 1
#@ assigns \nothing
def touch(a: List[int]) -> None:
    a[0] = 5
