r"""CARRIER — a READ-ONLY `Set[str]` parameter's membership does not type-check.

THIS FILE IS NOT A FALSE PROOF. It is a CAPABILITY GAP, gated the same way an open route's
carrier is, so that the day it starts working somebody has to say so.

    def has(held: Set[str], m: str) -> int:
        if m in held:
            return 1
        return 0

    This expression has type string, but is expected to have type int

`module6_whyml/functions.py` ~137 decides a set parameter's key type:

    _sk = "string" if (_mut_coll and kt.get(arg) == "string") else "int"

A MUTATED (by-reference) `Set[str]` parameter is string-keyed; a read-only one "must STAY
`map int`", because it is forwarded to sibling `val` bridges typed `map int` — and the
comment names the missing piece itself: *"that cross-method κ=string agreement is the
deferred I4 fixpoint"*. Module 5 has already tagged this parameter κ=string from the
membership (`_tag_str_keyed`); only Module 6's gate withholds it.

ITS TWO CONTROLS PIN THE MECHANISM FROM BOTH SIDES:
  `setelem-control-mutated-str-set-membership.py`  — the SAME membership, on a parameter the
      body also `.add`s to, VERIFIES. The mutation is what buys the string key.
  `setelem-control-int-set-membership.py`          — `Set[int]` membership VERIFIES, so the
      membership path itself is fine; it is typed to `int`, always.

WHEN THIS FILE STARTS VERIFYING, the I4 fixpoint has landed. Move it and its controls into
the corpus as witnesses in the SAME commit, lower `check-open-route-carriers.py`, and record
the mirror re-proof bill (the one-line version of the fix fails at the first call edge:
`module6_whyml/statements.py` line 1350, where the promoted `local_refs` is passed to a `val`
still declared `map int (option int)`).

`getting-better/open-routes/finding-a-set-has-no-element-type-and-no-union.md`
"""
_ = 0  # anchor
from typing import Set


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def has(held: Set[str], m: str) -> int:
    if m in held:
        return 1
    return 0
