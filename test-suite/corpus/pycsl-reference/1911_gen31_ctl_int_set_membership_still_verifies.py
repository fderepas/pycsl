r"""Test 1911 — gen #31 (expected PASS): CONTROL for `1909` — `Set[int]` membership.

`Set[int]` membership on a read-only parameter verified BEFORE the I4 fixpoint, because the
element type it needed was the one the lowering always used. It must still verify after.

This is the control that PINS THE LOCALISATION: it says the membership PATH was never the
defect. `1909` failed and this did not, on the same lowering, differing only in the element
type — so the defect was the ELEMENT TYPE and nothing else, and a fix that repaired the path
instead would show up here as a change.

IF THIS FILE EVER FAILS, the set membership lowering has broken generally and `1909`'s
localisation is no longer the right one.
Was `getting-better/open-routes/setelem-control-int-set-membership.py`.
"""
# pycsl-expected: PASS
_ = 0  # anchor
from typing import Set


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def has(held: Set[int], m: int) -> int:
    if m in held:
        return 1
    return 0
