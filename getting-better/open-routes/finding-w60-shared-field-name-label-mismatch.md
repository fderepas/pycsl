# FINDING (gen #10, 2026-09-12) — TWO RECORD CLASSES THAT SHARE A FIELD NAME EMIT AN UNBOUND
# FIELD READ, AND THE WHOLE FILE IS REFUSED

**NOT A ROUTE — FAIL-CLOSED.** Recorded because it is a real, reproducible completeness defect
that will keep costing driver-writing time until it is fixed, and because it nearly corrupted a
witness: route #85's positive witness (1219) failed for THIS reason and not for the reason it
was testing.

## THE DEFECT

When two record classes in one file declare a field with the SAME NAME, the emitter
disambiguates the WhyML field labels but does not carry the disambiguation into the field READ:

```whyml
  type c = { mutable c_d: map int (option int) }
  type e = { mutable e_d: map int (option int) }

  let f () : int =
    let c = { c_d = (const (None: option int)) } in      (* literal: DISAMBIGUATED label *)
    if (match Map.get (c.d) (1) with ...)                (* read:    BARE name -> UNBOUND *)
```

`c.d` is not a field of `c`, so Why3 rejects the file and every claim in it is refused.

## REPRODUCED AT THE BASELINE, SO IT IS NOT NEW

Verified at `cc01d463` (before gen #10's #85/#86 work) in a clean worktree: the same emission
appears, so this pre-dates the dict-field repairs and is not a regression from them. Two
classes, each with a field `d`, are enough — the field type does not matter to the mismatch.

## WHY IT IS NOT A SOUNDNESS ROUTE

The mismatch produces an UNBOUND SYMBOL, which is a Why3 type error, which refuses the whole
file. It cannot prove anything false; it can only refuse things that should prove. That is the
fail-closed direction, so it is an incompleteness finding, not a #69-class route.

## WHY IT IS WORTH FIXING ANYWAY, AND THE HAZARD IT CREATES FOR THIS CAMPAIGN

**IT SILENTLY TURNS A POSITIVE WITNESS INTO A FAILING ONE FOR THE WRONG REASON.** This campaign
relies on POSITIVE (must-still-prove) witnesses to bound repairs against over-broadness — 1211,
1215 and 1219 are all of that kind. A driver that refuses for an unrelated reason looks exactly
like a repair that went too wide, and the natural reaction — weaken the repair — would be
wrong. **WHEN A POSITIVE WITNESS FAILS, DUMP THE EMISSION BEFORE TOUCHING THE REPAIR.** Here
the dump named the cause in one line.

## REOPENING / FIX CONDITION

Fixing it means making the field READ use the same label the record literal and type
declaration use. Any such fix MUST be byte-diffed: the disambiguation only triggers on a shared
field name, so most of the corpus is untouched, but the label function is shared.

## A SECOND, ADJACENT COLLISION FOUND THE SAME WAY (and it cost a second iteration)

Renaming the colliding field to `e` on a class `E` did NOT fix witness 1219 — it produced

    type e = { mutable e: map int (option int) }
    let e = { e = ... } in ... e.e

and Why3 answered *"This expression has type PyCSL_Program.e, it cannot be applied"*. **A FIELD
NAME THAT COLLIDES WITH ITS OWN RECORD'S TYPE NAME (the class name, lowercased) IS ALSO
REFUSED.** Both collisions are fail-closed and both are invisible until you read the emission.

The practical rule for anyone writing drivers in this campaign: **give every class in a
multi-class driver DISTINCT field names, and never name a field after its class.** Witness 1219
uses `d` and `empty_map` for exactly this reason.
