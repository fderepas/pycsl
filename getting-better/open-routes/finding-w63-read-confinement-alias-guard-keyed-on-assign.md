# FINDING w63 — the READ-confinement alias guard is keyed on `ast.Assign`, so
# `return self.<field>` and `f(self.<field>)` escape it — NOT exploitable today,
# and the defender is the VALUE MODEL, not this pass

**CLASSIFIED HONESTLY: a CERTIFIED BOUNDARY / TCB-accounting finding, NOT a route.**
No falsehood is provable today. Recorded because its reopening condition is owned by a
*different subsystem*, which is route #89's exact failure mode.

## THE PROPERTY AND THE GUARD

`#@ happy key_confine: region 0 .. 64 / reads self.disk outside region / except _read_key`
is a **confidentiality** meta-property: the key bytes `[0, 64)` may be read only by
`_read_key`. (macsl twin: `\context(\reading)`.) `_weave_happy`'s `reading` branch realises it
with a per-READ-site `#@ check (idx < 0 or idx >= 64)`, and — because a per-site check can be
evaded by aliasing the array out of the method — adds an explicit alias rejection whose own
comment states the threat model:

> *"we also forbid the full-path alias `x = self.<field>` (a read through `x` would evade the
> per-read check — **closing a gap the shipped R1 write form leaves**)"*

**That parenthesis is independent corroboration of route #91**: the author knew the write form
had the gap and closed it only on the read side.

## THE GAP

The guard matches `isinstance(n, ast.Assign)`:

```python
if (isinstance(n, ast.Assign)
        and isinstance(n.value, ast.Attribute)
        and isinstance(n.value.value, ast.Name)
        and n.value.value.id == "self"
        and n.value.attr == hp.field):
```

So it sees `x = self.disk` and nothing else. A whole-field read that is **not an assignment**
escapes it — measured, both shapes **VERIFY**:

| non-exempt shape | guard fires? | file |
|---|---|---|
| `x = self.disk` | YES (hard error) | — |
| `def leak(self) -> list: return self.disk` | **NO** | **VERIFIES** |
| `return self.peek(self.disk)` (field as a call argument) | **NO** | **VERIFIES** |

Controls (run first, per the vacuity rule): **0715 PROVES** and **0716** (an in-region point
read) **REFUSES**, so the read-confinement machinery is live in this exact shape.

## WHY IT IS NOT A ROUTE — MEASURED, NOT ASSUMED

The escape hands the array out, but the caller **cannot recover a protected byte**:

```python
#@ requires self.disk[0] == 7
#@ ensures \result == 7
def exfil(self) -> int:
    a = self.leak()
    return a[0]
```
**REFUSED** (`Unknown` — it emitted, the prover could not derive it). The value model does not
propagate array *identity* through a return, so `a` is not `self.disk` and nothing about the
protected region follows. Same defender as route #91's alias axis, and the same spec sentence
names it: §2.5, *"value-semantic arrays bar local-alias escape."*

**A VACUITY TRAP I WALKED INTO AND HAD TO BACK OUT OF — the fourth this campaign has caught.**
My first exfiltration probe put `#@ ensures \result == a[0]` on a *method* with a `list`
parameter and both directions failed with `unbound function or predicate symbol
'subscript_get'`. A set of refusals is not evidence, so I isolated it: the same contract on a
**module-level function** (`iso1`) **PROVES**. So the failure was an incidental emission gap in
`<method> + list param + subscripted contract`, not a fence — and had I stopped one step
earlier I would have filed "fail-closed" for entirely the wrong reason. **AN INCIDENTAL
EMISSION FAILURE AND A DELIBERATE FENCE ARE INDISTINGUISHABLE AT THE COMMAND LINE; THE ONLY
THING THAT SEPARATES THEM IS A CONTROL THAT MOVES ONE VARIABLE.** (Side finding, unaudited:
`ensures \result == a[0]` on a `self`-bearing method with a `list` parameter emits an unbound
`subscript_get`. Not chased — recorded for whoever needs it.)

## REOPENING CONDITION — AND WHY THIS ONE IS WORTH WATCHING

**The day the value model propagates collection identity through a return or an argument
(reference semantics for collections), the read-confinement property becomes provable while a
non-exempt method hands the entire protected region to an arbitrary caller.** The guard that
should stop it exists but is keyed on `ast.Assign` and will not fire on a `Return` or a `Call`
argument. Reference semantics for collections is a *completeness* goal that nobody would think
of as touching a confidentiality gate — which is precisely route #89's lesson.

## HARDENING APPLIED (see the progress log)

Unlike #91's alias axis — where no guard existed and the case is ill-typed, so a new guard
could not be negative-tested — here the guard **already exists** and is merely keyed too
narrowly, and widening it IS negative-testable: the observable is the *rejection*, which does
not depend on exploitability. Measured corpus cost first: **no read-confinement corpus file
performs a whole-field return or passes the field as an argument**, so the widening is inert.
