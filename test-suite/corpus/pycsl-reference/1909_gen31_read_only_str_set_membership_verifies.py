r"""Test 1909 — gen #31 (expected PASS): a READ-ONLY `Set[str]` parameter's membership.

WAS A CARRIER, NOT A TEST. This file spent a generation as
`getting-better/open-routes/setelem-carrier-read-only-str-set-membership.py`, gated FAILED by
`bin/check-open-route-carriers.py`, with the instruction written into it:

    WHEN THIS FILE STARTS VERIFYING, the I4 fixpoint has landed. Move it and its controls into
    the corpus as witnesses in the SAME commit.

WHAT IT USED TO DO:

    This expression has type string, but is expected to have type int

`module6_whyml/functions.py` decided a set parameter's key type with

    _sk = "string" if (_mut_coll and kt.get(arg) == "string") else "int"

A MUTATED (by-reference) `Set[str]` parameter was string-keyed; a read-only one had to STAY
`map int`, because it is forwarded to sibling `val` bridges typed `map int` — and the comment
named the missing piece itself: *"that cross-method κ=string agreement is the deferred I4
fixpoint"*. Module 5 had already tagged this parameter κ=string FROM THE MEMBERSHIP
(`_tag_str_keyed`); only Module 6's gate withheld it, and the gate had to withhold it because
a usage-derived κ is not something the other end of a call edge can know.

THE FIX IS NOT A FIXPOINT. `_m5_get_field_key_type` (record FIELDS) already covered
`Set[str]`, and says why in its own docstring — **a set's element IS its key** — while
`_m5_get_dict_key_type` (PARAMETERS) covered only `Dict[str, V]`. One rule, stated twice,
implemented once. Reading κ from the DECLARATION in the parameter extractor makes both ends of
a call edge agree BY CONSTRUCTION: no propagation pass, no fixpoint, nothing to converge.

ITS TWO CONTROLS ARE `1910` (the same membership on a MUTATED param, which verified before the
fix and must still verify) and `1911` (`Set[int]` membership, which verified before and must
still verify — the membership PATH was never the defect, the ELEMENT TYPE was).

`getting-better/open-routes/finding-a-set-has-no-element-type-and-no-union.md`
"""
# pycsl-expected: PASS
_ = 0  # anchor
from typing import Set


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def has(held: Set[str], m: str) -> int:
    if m in held:
        return 1
    return 0
