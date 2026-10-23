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

WHEN THIS FILE STARTS VERIFYING, THE DEFINITION SIDE IS FIXED — AND THAT IS NOT THE ROUTE.
Corrected 2026-09-25 by doing exactly what this paragraph used to say. The TWO-part patch —
read the key type from the DECLARATION in the parameter extractor (`_m5_get_field_key_type`
instead of `_m5_get_dict_key_type`), then drop the `_mut_coll` conjunct — flips this carrier,
holds BOTH controls, and proves three new corpus witnesses. It also breaks FOUR mirror files
in thirty seconds, every one of them with

    This expression has type string -> option.Option.option int,
    but is expected to have type int -> option.Option.option int

a promoted `map string` reaching a sibling `val` BRIDGE still declared `map int`. The old note
here predicted that shape for the ONE-line version and expected the two-line version to remove
it "by construction". It does not: **a bridge has no Python declaration to read** — it is
synthesised for a method the emitter did not lower, and its parameter types come from whatever
the emitter believed when it wrote the bridge. Promoting the definition side moves one end of
the call edge and leaves the other.

THE CONDITION THAT MEANS THE FIXPOINT HAS LANDED IS THE BILL: this file verifies AND all TEN
moved mirror files still prove — `Module6_WhyMLTranspiler`, `frontend/__init__`,
`frontend/ir_resolve`, `frontend/monomorphize`, `module6_whyml/expr_ghost_collections`,
`expr_ghost_spec_ops`, `expressions`, `functions`, `statements`, `stmt_control_flow`. Only then
move this file and its controls into the corpus and lower `check-open-route-carriers.py`.
See `getting-better/open-routes/finding-the-i4-fixpoint-really-is-a-fixpoint.md`.

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
