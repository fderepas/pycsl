# ROUTE #86 — A `map int (option int)` PARAMETER COERCION SUBSTITUTES THE **EMPTY MAP** FOR
# THE ACTUAL, AND THE CALLEE'S CONTRACT IS THEN EVALUATED AGAINST IT

**STATUS: FOUND AND REPRODUCED 2026-09-12 (gen #10), AT HEAD. BOTH DIRECTIONS MEASURED ON TWO
CARRIERS. REPAIR BUILT. OPEN (gating).**

**CLASS: the #69 class** — a FALSE POSTCONDITION about ordinary, TOTAL Python.

**THIS IS CARVE-OUT CENSUS CANDIDATE 5 PROPER**, the arm gen #9 ranked in the LOW-VALUE TAIL
and left unprobed, and it is a DIFFERENT DEFECT from route #85 even though the two produced
the *same wrong constant*.

## THE CARVE-OUT, VERBATIM (`module6_whyml/expressions.py`, the `map int (option int)` arm)

> "No known int→map coercion. Use `const None` as a placeholder empty map; the abstract val
> has no axioms about its contents anyway."

**THE JUSTIFICATION IS A CLAIM ABOUT THE CALLEE BEING ABSTRACT, NOT ABOUT THE LOWERING**, and
it stops being true the moment the callee is a REAL emitted function carrying a contract. An
actual that is neither a bare identifier nor an already-map expression — a FIELD READ `c.d`,
for instance — falls to the `else` and is replaced by the totally empty map.

## THE DEMONSTRATION — AND WHY IT ONLY BECAME VISIBLE AFTER #85 WAS FIXED

With route #85 repaired, the emitted WhyML for the cross-call carrier reads:

```whyml
  let f () : int
    ensures  { (result = 0) }
  =
    let c = { d = (map_update_some (const (None: option int)) 1 5) } in   (* CORRECT *)
    (g (const (None: option int)))                                        (* WRONG   *)
```

**The record now carries the RIGHT map and the call still passes the EMPTY one.** Before #85's
repair both were `const None`, so the two erasures were INDISTINGUISHABLE — one masked the
other, and any probe would have credited the whole effect to whichever one it fixed first.

| carrier | claim | CPython | PyCSL |
|---------|-------|---------|-------|
| VALUE — callee has `ensures (1 in d) ==> \result == 1` | `\result == 0` | **1** | **PROVED** ❌ |
| VALUE, TRUE twin | `\result == 1` | 1 | refused |
| **REQUIRES-DISCHARGE** — callee has `#@ requires 1 not in d` | `\result == 0` | **the program VIOLATES that precondition** | **PROVED** ❌ |

## THE REPAIR

The `else` arm emits a POLYMORPHIC UNCONSTRAINED map (`val any_map (_u: unit) : map 'k (option
'v)`) instead of `const None`. **"No known coercion" must mean "nothing is known", not "it is
empty"** — an erasure to a DEFINITE value is what makes this family dangerous, and an erasure
to an UNCONSTRAINED one is merely incomplete. Polymorphic on purpose: the parameter may lower
to `map string (option int)` or carry a `value_type`, and a monomorphic `any` would be
ill-typed there — fail-closed, but needlessly so.

Both the false claim and the true twin are now refused, which is honest: this arm genuinely
does not know the actual's contents, which is why a placeholder was wanted in the first place.

## THE LESSON — NEW, AND THE MOST TRANSFERABLE THING IN THIS PAIR OF ROUTES

**TWO INDEPENDENT ERASURES THAT PRODUCE THE SAME WRONG VALUE ARE INDISTINGUISHABLE UNTIL ONE
OF THEM IS FIXED, AND FIXING ONE IS THEREFORE A MEASUREMENT INSTRUMENT FOR THE OTHER.** Route
#85's repair did not merely close #85: it turned #86 from invisible into a one-line read of
the emitted file. The practical rule: **after landing a repair, RE-RUN THE CARRIERS AND LOOK
FOR ONE THAT STILL PROVES — a surviving carrier is not a failed repair, it is a second route
that the first one was masking.** Here, the cross-call carrier survived #85's repair, and that
survival was the entire finding.

Corollary for verdict-reading: "the repair closed 3 of 4 carriers" should never be recorded as
a partial success. It is a *hypothesis that the fourth carrier has a different cause*, and it
is cheap to settle by dumping the emission.

## WITNESSES

`scratchpad/w60/r86/v1_value.py`, `v1_twin.py`, `scratchpad/w60/r85/c4_discharges_requires.py`.
