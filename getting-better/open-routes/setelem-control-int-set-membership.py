r"""CONTROL for `setelem-carrier-read-only-str-set-membership.py` — `Set[int]` membership on
a READ-ONLY parameter, which VERIFIES today.

The carrier fails on a `Set[str]`; this file is the same program one element type over. It
VERIFIES, which is what says the membership PATH is fine and the defect is the ELEMENT TYPE:
membership is lowered against `map int`, always, so an `int` element passes it and a `str`
element cannot.

IF THIS FILE EVER FAILS, the set membership lowering has broken generally and the carrier's
localisation is no longer the right one.
"""
_ = 0  # anchor
from typing import Set


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def has(held: Set[int], m: int) -> int:
    if m in held:
        return 1
    return 0
