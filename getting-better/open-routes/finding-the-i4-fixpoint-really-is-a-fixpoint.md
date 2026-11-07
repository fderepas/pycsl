# The I4 "fixpoint" really is a fixpoint — the two-line version breaks four mirror files in thirty seconds

Generation #31, 2026-09-25T08:03Z. **A LANDED-AND-REVERTED increment, recorded because the
reversal is the measurement.**

## What was claimed

`module6_whyml/functions.py` gated a set parameter's key type on whether the body MUTATED it:

    _sk = "string" if (_mut_coll and kt.get(arg) == "string") else "int"

with the comment naming the missing piece — *"that cross-method κ=string agreement is the
deferred I4 fixpoint"*. A read-only `Set[str]` parameter had to stay `map int` because its key
type could only come from the USAGE tagger, and a usage-derived key type is not something the
other end of a call edge can know.

The prepared two-part patch claimed to remove the need for a fixpoint:

1. the PARAMETER key-type extractor calls `_m5_get_field_key_type` (which already covered
   `Set[str]` — *a set's element IS its key*) instead of `_m5_get_dict_key_type`;
2. the `_mut_coll` conjunct goes away, because with the key type read from the DECLARATION,
   **both ends of a call edge get it from the same place**.

## What the carriers said, and what they could not say

    setelem-carrier-read-only-str-set-membership   FAILED/REFUSED  ->  SUCCESS
    setelem-control-mutated-str-set-membership        SUCCESS      ->  SUCCESS
    setelem-control-int-set-membership                SUCCESS      ->  SUCCESS

The carrier flipped. Both controls held. Three new corpus witnesses proved individually. The
marker count and the verbatim population were unchanged, as an emitter change should leave
them. **Everything a carrier can check, checked.**

## What the bill said, four seconds in

    module6_whyml/expr_ghost_spec_ops.py    *** NOT PROVED ***  (4 s)
    module6_whyml/expr_ghost_collections.py *** NOT PROVED ***  (3 s)
    frontend/monomorphize.py                *** NOT PROVED ***  (7 s)
    module6_whyml/stmt_control_flow.py      *** NOT PROVED *** (12 s)

and all of them the same shape:

    This expression has type string -> option.Option.option int,
    but is expected to have type int -> option.Option.option int

**A promoted `map string` reaching a sibling `val` bridge still declared `map int`.** That is
precisely the desync the `_mut_coll` conjunct existed to prevent. Not a proof failure — a Why3
TYPE error. The mirror does not compile.

## Why "both ends read the declaration" is not true

A `val` BRIDGE has no Python declaration to read. It is synthesised for a method the emitter
did not lower — an abstract stub standing in for a sibling — and its parameter types come from
whatever the emitter believed when it wrote the bridge, not from an annotation. So promoting
the key type on the DEFINITION side moves one end of the edge and leaves the other where it
was. The declaration is a better source than the usage tagger, and it is still only one end.

**The fixpoint was not deferred out of laziness. It is load-bearing**, and the shape of the
real work is now visible: every `val` bridge for a collection-carrying method has to be
re-typed in the same pass that promotes the definitions, which is a whole-module agreement
problem — i.e. a fixpoint.

## What this cost, and what it bought

Landed at 07:58Z (`eaf118fd`), reverted at 08:03Z (`ca6c0216`), five minutes, no gate wasted
past its first stage. The refusal written into the plan before any edit is what made the
reversal automatic rather than a decision:

> If a moved mirror file stops proving, the increment does NOT land by marking that file
> `\trusted`. That would be trading a real proof for a marker in order to buy a capability —
> the exact inverse of this campaign. Record the regression and stop.

**AND THE THIRD "NECESSARY BUT NOT SUFFICIENT" OF THE SESSION.** A `--no-proof` LOWERS is not a
proof. A green whole-file proof is not a conversion. **And a carrier that flips is not a
capability.** Each one is a cheap gate that answers a real question and answers only that
question; the expensive gate behind it is the one that decides. This session found all three by
running the expensive one anyway.

## The carrier is back, and it now knows more

The three files are back in `getting-better/open-routes/` and
`check-open-route-carriers.py` is back to 8 rows. The carrier's instruction — *"when this file
starts verifying, the I4 fixpoint has landed"* — is now known to be WRONG as written: the
carrier verifying means the DEFINITION side is fixed, and says nothing about the bridges. The
condition that means the fixpoint has landed is the bill: **all ten moved mirror files still
prove.**
