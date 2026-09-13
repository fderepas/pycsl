# ROUTE #95 — A COMPOSER METHOD THAT SHADOWS A MIXIN PROVIDER SKIPS THE CLONE, AND WITH IT
# THE ONLY THING THAT WAS EVER CHECKING `provider ⊑ dependency` (S2b)

**SEVERITY 1. FOUND, REPRODUCED, AND CONTRADICTED BY AN EXECUTED CPYTHON RUN.**
**This is finding w66's reopening condition arriving early: w66 concluded S2b is unimplemented
but COMPENSATED by flatten-and-re-verify. There is a shape in which the flattening never
happens, and w66 did not probe it — the compensator has a hole of its own.**

## THE MECHANISM

`ir_resolve.apply_composition` flattens each mixin's `provides` method into the composer:

```python
tail = f["name"][len(m) + 2:]
new_name = f"{c}__{tail}"
if tail in own_tails or new_name in existing:
    continue   # composer overrides it, or already cloned
```

`own_tails` is computed BEFORE the loop from the composer's OWN methods. So **if the composer
defines a method with the same tail as a mixin provider, the provider is never cloned.** The
clone is the ONLY mechanism that ever re-verifies a provider against the concrete composer
(w66's whole compensating argument), and `composed_provider_methods` — the set Module 6 uses to
resolve `self.<tail>(…)` to a CONCRETE function — never gains the name either. So inside the
cloned sibling, `self.emit(k)` keeps resolving to an **abstract `val` carrying the DECLARED
DEPENDENCY's contract**, while at run time it is the composer's own, weaker method.

**The dependency contract is ASSUMED at the call site and DISCHARGED BY NOBODY.**

## THE EXPLOIT — VERIFIES, AND CPYTHON SAYS IT IS FALSE

`CoreEmit provides emit ensures \result == 0`; `MapOps depends_method emit ensures \result >= 10`
and `provides handle_get ensures \result >= 10` with body `return self.emit(k)`;
`Facade compose_from CoreEmit, MapOps` **defines its own `emit` returning 0** and
`run ensures \result >= 10` with body `return self.handle_get(k)`.

| driver | verdict |
|---|---|
| **A — flagship 0549, unmodified (POSITIVE CONTROL: is the algebra alive?)** | **PROVES** |
| **B — the same exploit WITHOUT the composer's own `emit`** (gen #13's w66 probe) | **FAILS** — the compensator works |
| **C — the exploit, composer defines its own `emit`** | **PROVES `\result >= 10`** |
| **CPython, same shape with the mixins as real bases** | **`Facade().run(5) == 0`** |

`0 >= 10` is FALSE. A proved postcondition contradicted by an executed run — the #94 evidence
class, the strongest this campaign produces.

**B vs C differ by exactly one method.** That is the whole route: the composer's own `emit` is
not an override that gets checked, it is an override that DELETES the check.

## WHY THE DIFFERENTIAL PINS THE MECHANISM

Facade's own `emit` promises `\result == 0`. If the cloned `handle_get` were resolving
`self.emit` to it CONCRETELY, the clone could not possibly prove `\result >= 10`. It proves. So
the clone is being verified against the **abstract dependency** `ensures \result >= 10` — the
very obligation S2b was supposed to check and does not.

## WHY `if tail in own_tails: continue` LOOKS CORRECT

It reads as ordinary override semantics — "the composer's own definition wins" — and for
DISPATCH that is exactly right. What it silently also does is remove the method from the
re-verification population. **The line conflates "the composer supplies this" with "this needs
no checking", and those are opposites: a composer-supplied provider is the one implementation
that was NEVER verified against the dependency, because it never went through a mixin's S1.**

>>> **A COMPENSATING MECHANISM THAT IS NOT A CHECK HAS NO OBLIGATION TO BE TOTAL, AND WILL NOT
>>> BE.** w66 was right that flatten-and-re-verify discharges S2b — on the population it
>>> flattens. Nothing made that population equal to the population S2b was about, because
>>> nothing ever wrote S2b down. **When you certify a missing check as "covered by another
>>> mechanism", the next question is not "does it cover this case" but "what is its population,
>>> and who keeps it equal to the check's?"**

## REPAIR (landed with this route)

Sound-by-rejection, and the sibling discipline is already in this function (unique-provider and
field-classification are both hard `PyCSLSemanticError`s): **a composer method that shadows a
composed mixin's `provides` tail is REJECTED** when any mixin declares a `depends_method` /
`requires_method` on that tail, naming the unverifiable refinement. Rejecting rather than
resolving is forced: injecting the dependency contract onto the composer's own method would
ASSUME what S2b exists to prove.

## REOPENING CONDITION

Tier-2 `#@ resolve <m> from <Mixin>`, or any future support for a composer legitimately
overriding a provider, must discharge `composer-method ⊑ declared-dependency` explicitly —
that is S2b, and at that point it must be IMPLEMENTED, not compensated.

## THE BOUNDARY, SHARPENED — INHERITING THE SHADOWING METHOD IS **NOT** A ROUTE (MEASURED)

The obvious sibling shape — the composer does not DEFINE the weak method but INHERITS it from a
base class — is more natural than the exploit above and was worth measuring, because
`apply_inheritance` runs before `apply_composition` and could plausibly have populated
`own_tails`.

| driver | verdict |
|---|---|
| `Facade(WeakBase)` with `WeakBase.emit ensures \result == 0`, dependency `>= 10` | **FAILS** |
| **POSITIVE CONTROL: the same file with every claim weakened to `>= 0`** | **PROVES** |

The control proves, so the inheritance+composition channel is ALIVE and the refusal above is a
real fence, not a dead channel. (Per the campaign rule: a set of refusals is not evidence until
one thing proves — four vacuity traps were caught this way last generation.) The mechanism is
visible in the control's goal list: **`facade__emit'vc` EXISTS**, i.e. the provider was cloned
into the composer anyway, and therefore re-verified against the concrete facade.

>>> **SO THE ROUTE IS SPECIFICALLY "THE COMPOSER DEFINES IT ITSELF", NOT "THE COMPOSER HAS IT".**
>>> An inherited method does not enter `own_tails`, the clone still happens, and the
>>> compensating re-verification still fires. That is exactly the kind of distinction that gets
>>> lost when a repair is scoped from a description rather than from a measurement — and it is
>>> why the landed check is keyed on `own_tails` (the population the flatten loop actually
>>> consults) rather than on "does the composer have a method named `pm`", which would have
>>> rejected this safe, working shape.
