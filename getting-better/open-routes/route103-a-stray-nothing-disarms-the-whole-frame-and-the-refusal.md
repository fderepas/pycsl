# ROUTE #103 — A STRAY `#@ assigns \nothing` BESIDE A REAL TARGET DISARMS **BOTH** THE FRAME **AND** ROUTE #98's REFUSAL

**Severity 1. CLOSED gen #18 (2026-09-13). ORDER 2 — the carrier is the campaign's own repair.**

## THE ONE-LINE STATEMENT

`Module5_IREmitter` flattens EVERY `#@ assigns` clause of a function into ONE list, so a
function spelling `#@ assigns g[0..1]` on one line and `#@ assigns \nothing` on the next
arrives at `_emit_frame_condition` with `nothings` non-empty *and* a real target. Both guards
there were written `... and not nothings`, so ONE clause silenced the OTHERS: the real `writes`
was dropped **and** route #98's refusal was skipped. The `val` came out pure.

```
if _unframed_regions and not nothings:   -> route #98's refusal SKIPPED
if _val_targets     and not nothings:    -> the real `writes` DROPPED
```

## BOTH DIRECTIONS MEASURED

| arm | verdict |
|---|---|
| FALSE fact `ensures \result == 7`, at 5795cfef | **PROVES** |
| the same file after route #101's repair | **STILL PROVES** — it SURVIVED the repair |
| CPython ground truth | returns 5 |
| after the #103 repair | **REFUSED**: `PYCSL-CONTRADICTORY-ASSIGNS` |

## WHY ORDER 2

Unlike #101 and #102, the carrier here is a CAMPAIGN ARTEFACT. `and not nothings` was written
by **route #96's own repair**, to keep `\nothing` meaning "writes nothing". The intent was
right; the scope was one conjunct too wide.

>>> **A REPAIR THAT ADDS A GUARD CONDITION ADDS AN `AND`, AND EVERY `AND` IS A WAY FOR ONE
>>> CLAUSE TO SWITCH OFF ANOTHER. When you write `if X and not Y`, ask who else can set `Y`.**

## THE REPAIR IS A REFUSAL, NOT A PRECEDENCE RULE

`assigns \nothing` beside `assigns g[0..1]` is not an under-specification to be resolved by
picking a winner: the clauses CONTRADICT, and any winner the emitter picks is a guess about
what the reviewer who certified the stub meant.

**CENSUS FIRST — THE POPULATION IS THE THING NOBODY RE-READS.** A repo-wide scan of every
contiguous `#@ assigns` block found **ZERO** functions mixing `\nothing` with a real target.
So the refusal has an EMPTY live population and is byte-inert — and **a guard whose population
is empty has checked nothing and looks exactly like a guard that passed**, which is why it is
negative-tested directly by witness 1291.

## AND THE REFUSAL MESSAGE'S FIRST DRAFT RECOMMENDED ITS OWN EXPLOIT

The message ended *"Delete the `assigns \nothing` clause, or delete the write target(s)."*
The second half is the exploit: deleting the targets leaves a `\nothing` that **nothing
verifies on a bodyless `val`** — the emitter merely READS it — landing you on exactly the pure
`val` the refusal exists to prevent. This is ranked generator #1 (route #90's shape) firing on
the campaign's own remediation text, caught before landing. The discriminator held: *advice
naming conditions the emitter CHECKS is safe; advice naming a marker it merely READS is the
hazard.* Rewritten to recommend only the checked repair.

## RESIDUE, NAMED

The NON-val path still returns `ensures { !h = old !h }` when `nothings` is non-empty,
ignoring any real region alongside it. That is fail-CLOSED for a real body — Why3 infers the
writes from the body and the `ensures` simply fails to prove — so it is not exploitable, but
it is the same shape and is recorded here rather than left implicit.

## REOPENING / CLOSING CONDITION

CLOSED: witness `1291_route103_a_stray_nothing_disarmed_the_whole_frame.py` PROVED at 5795cfef
and is REFUSED at HEAD. REOPENS if `\nothing` is ever given precedence semantics instead of
being treated as a contradiction, or if a new guard is written `and not nothings`.
