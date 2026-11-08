# FINDING — `core_ir_semantic` DOES NOT PROVE, AND ALL EIGHT UNPROVEN GOALS ARE
# TERMINATION OF A WALK OVER AN UNTYPED VALUE
# (measured 2026-09-09/10 by relaunch #51; battery `w51_cis`, rc=1)

## WHAT WAS MEASURED

`w51_cis` is the **first-ever** whole-file proof of
`src/self-annotate/src/core_ir_semantic.py`. There is no prior green, so this is a FIRST
MEASUREMENT and not a regression — an important distinction, because the file carries
route #51's two new Module 4 functions and it would be easy to mis-read this as route
#51 having broken something.

Eight goals remain unproven and every one of them is a TERMINATION sub-goal:

    6x   termination of goal walk'vc
    1x   termination of goal _returns_literal_none'vc
    1x   termination of goal _check_scalar_return_annotation'vc

All eight are **Timeout (30.00s)** at 48-60 MILLION steps — the prover grinding, not
refuting. Nothing here says the code is wrong; it says the model cannot show it stops.

## THE CAUSE, READ OUT OF THE SOURCE

```python
#@ requires True
#@ ensures True
#@ assigns \nothing
def _returns_literal_none(body) -> bool:          # <-- `body` has NO annotation
    found = [False]

    def walk(node):                               # <-- nested, structurally recursive
        ...
        if isinstance(node, dict):
            ...
            for x in node.values():
                walk(x)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(body)
    return found[0]
```

`walk` descends through `node.values()` and through list elements with **no well-founded
measure**, over a parameter that has **no type at all**. Why3 cannot prove a structural
walk terminates when the thing being walked has no type to measure. `walk`'s termination
is therefore unprovable as written, and its two enclosing functions inherit the failure —
`_check_scalar_return_annotation` only because it calls `_returns_literal_none`.

## WHY IT MATTERS RATHER THAN BEING A COSMETIC GAP

Both `_returns_literal_none` and `_check_scalar_return_annotation` are **un-`\trusted`**
and carry `#@ requires` / `#@ ensures` / `#@ assigns` contracts. So the campaign's
bookkeeping COUNTS THEM AS BODY-VERIFIED while their termination is not proved. That is
the same shape as this window's L1 fidelity finding: a method sitting in the verified
column on a claim the planes do not actually establish. The honest options are to prove
it, or to stop counting it.

## CORRECTION — I CLASSIFIED THIS TOO HARSHLY ON FIRST READING, AND THE FILE ITSELF
## REFUTES THE HARSH VERSION

My first classification said "no amount of prover time discharges a termination VC for a
recursion with no decreasing measure" and called it a flat CORRECTNESS boundary. Reading
the proof log further refutes that, and the refutation is in the SAME FILE:

    Sub-goal variant decrease of goal _union_c8_walk__d'vc
    Sub-goal variant decrease of goal _union_c8_walk__cases'vc
    Sub-goal variant decrease of goal _check_union_narrowing__collect'vc

`core_ir_semantic` contains OTHER structural walks that emit `variant decrease` goals —
i.e. they HAVE variants, and the machinery for giving a walk a well-founded measure is
present and working in this very file. So "the model cannot do this" is false.

**THE ACTUAL DIFFERENCE IS THE PARAMETER TYPE.** `_union_c8_walk(stmts: list,
union_vars: set, fname: str)` is fully annotated and walks a TYPED, HOMOGENEOUS structure.
`_returns_literal_none(body)` is annotated NOWHERE, and its nested `walk(node)` is
HETEROGENEOUS by construction — it branches on `isinstance(node, dict)` versus
`isinstance(node, list)` and recurses into both, so even typing the outer `body: list`
would not give the inner `walk` a measure, because `walk`'s argument alternates between a
dict, a list and a scalar as it descends.

## CLASSIFICATION (§A.3's two-way test, applied freshly)

**A COST/SCALE boundary, NOT a correctness one — revised after the correction above.**
The technique is present and proving in the same file; what is missing is a TYPE on the
walked value. Under §A.3's test that is squarely the cost/scale side: it is a real,
bounded piece of work (give the walk a typed, measurable argument), not something the
value model cannot express. A funded window is exactly the budget that pays it.

What makes it more than a one-line annotation is that `walk` is HETEROGENEOUS: it descends
through dict values AND list elements AND stops at scalars. Giving it a measure means
giving it a single type that covers all three — which is precisely what the certified
IR-node ADT is for.

**THE REOPENING CAPABILITY IS SPECIFIC AND IT EXISTS**: type `walk`'s parameter at the
CERTIFIED IR-NODE ADT (the tier-1/2/3 ADT foundation this campaign banked) and give it the
structural `variant` an inductive type supports. The tree already does exactly this
elsewhere — `preamble.py`'s generated `term_eq` carries `variant { a }` over the certified
`term` inductive and proves. The obstacle is not that the technique is missing; it is that
`_returns_literal_none` takes a raw untyped `body` and would have to be retyped, which
changes a LIVE Module 4 function and therefore owes an L1 fidelity re-sync and a re-proof.

## THE INTERIM DISPOSITION AND ITS PRICE

Mark `_returns_literal_none` `\trusted` so the claim matches what is actually established,
and record this boundary. **The metric goes UP, 456 -> 457, and that is the CORRECT
direction**: the trust surface was always this big; only the bookkeeping said otherwise.
A campaign whose number can only go down has stopped measuring anything.
