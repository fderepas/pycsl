# ROUTE #91 — a HAPPY region-confinement property is PROVED while a non-exempt method
# replaces the entire protected region (whole-field rebinding was never a write site)

**STATUS: CLOSED, FAIL-CLOSED, 2026-09-13 (gen #13). SEVERITY 1.**
The violated claim is a *security meta-property* (a HILARE confinement guarantee), not a
value: `happy R: region LO .. HI / writes self.f outside region / except …` states that no
method outside `except` writes `self.f` inside `[LO, HI)`. It was provable while a
non-exempt method overwrote the whole region with caller-supplied contents.

## MECHANISM

`Module3_Weaver._weave_happy`, region-WRITE branch, clause (A) realises the property with a
per-site `#@ check` injected at every write site found by `_collect_field_sites`. That
collector defers to `_field_write_site`, which **requires the assignment target to be an
`ast.Subscript`** whose base is `self.<field>`:

```python
for tgt in targets:
    if not isinstance(tgt, ast.Subscript):
        continue                      # <-- a whole-field store falls straight through
```

A whole-field rebinding `self.disk = a` is an **`ast.Attribute`** target. It matched
nothing, so it received **no check at all** — while replacing the entire array, protected
region included, with an arbitrary caller-supplied one. Clause (A)'s comment calls itself
"a per-site `#@ check` at every direct write of the field"; a whole-array store *is* a
direct write of the field, and is the one kind a per-index check can never constrain.

## BOTH DIRECTIONS MEASURED — all in the SAME file shape, before the repair

| driver | claim | verdict |
|---|---|---|
| `wipe(self, a: list): self.disk = a`, non-exempt | file verifies at all | **VERIFIED** (the route) |
| + `requires a[1000] == 99`, `ensures self.disk[1000] == 99` | region took the attacker value | **PROVED** |
| + `requires self.disk[1000] == 7`, `ensures self.disk[1000] == 7` | region was preserved | **REFUSED** |
| `self.disk[1000] = v` (direct, in-region) | control: guard fires | **REFUSED** |
| `self.disk[3000] = v` (direct, out-of-region) | control: capability alive | **PROVED** |

The second and third rows are the teeth: **the value model itself certified that the
protected cell now held the attacker's value, and refused the claim that it was preserved,
while the property whose entire content is "it was preserved" was being proved.** The
fourth and fifth rows are the non-vacuity: the machinery demonstrably fires in this exact
file shape, and the capability the form exists to provide still works — so the route is not
a dead pipeline (the gen #12 rule: a probe whose own positive control refuses has measured
nothing).

## WHAT MAKES THIS ONE TRANSFERABLE — THE SIBLING FORMS ALREADY GUARDED IT

`_weave_happy` has three confinement forms. Laid side by side:

| form | direct subscript site | **whole-field rebind `self.f = e`** | alias `x = self.f` |
|---|---|---|---|
| `protects <paths>` | caught (dotted path) | **CAUGHT** — `_collect_protect_sites` matches `_target_dotted_path(tgt)`, and an `Attribute` target's dotted path IS the protected path | `x = self` (proper prefix) caught by `_check_protect_aliasing` |
| `reading` (H-I1) | caught (`_subscript_read_site`) | n/a (read form) | **CAUGHT** — an explicit rejection, with a comment saying the alias "would evade the per-site check" |
| **region-write (the primary form)** | caught | **MISSED — ROUTE #91** | no guard HERE, but defended by the VALUE MODEL per spec §2.5 (below) |

So the miss was not a design decision: **two sibling branches of the same function guard
exactly the write the primary branch missed, and one of them documents the evasion in
prose.** The `protects` form gets it right for free because it matches on the *dotted path*
rather than on the *syntactic shape of the target* — which is the generalisable lesson.

>>> **A CONFINEMENT CHECK KEYED ON THE SYNTACTIC SHAPE OF A WRITE TARGET ENUMERATES THE
>>> SHAPES ITS AUTHOR HAPPENED TO PICTURE. KEY IT ON THE PATH BEING WRITTEN INSTEAD, AND
>>> THE SHAPES TAKE CARE OF THEMSELVES.** The author pictured `self.f[i] = v` — the write
>>> the feature is *about* — and the whole-array store, which is strictly more destructive,
>>> was invisible precisely because it is not indexed.

## HOW IT WAS FOUND

The advice-bearing-refusal-message generator (gen #12's find), applied to its own #1 ranked
target — `Module3_Weaver.py:887/999`, *"Add `#@ \preserves` to promise it preserves the
protected fields"*. **The prescription itself turned out to be sound** (clause (C)
synthesizes a real, visible, honestly-labelled `(an assumed postcondition)` preservation
`ensures`, and the marker is gated on `trusted or abstract`, i.e. inside the declared TCB).
But reading the message put clauses (A) and (C) side by side in one screen, and the
*structural* comparison of the three forms — which guards which — was what paid.

>>> **AN ADVICE AUDIT THAT CLEARS ITS MESSAGE IS NOT A DEAD ROUND. THE MESSAGE IS A POINTER
>>> TO A GUARD; READ THE GUARD'S SIBLINGS WHILE YOU ARE THERE.** Four of the five advice
>>> messages audited so far have held. This one held too — and its neighbourhood held the
>>> route.

## REPAIR — sound-by-rejection, the discipline the sibling forms already use

Clause **(A2)**, inserted between (A) and (C) in the region-write branch: a non-exempt
function that rebinds the whole field is a hard error. A per-index check *cannot* constrain
a whole-array store, so there is nothing to defer — this is the same
"sound-by-rejection, not deferred" stance `_check_protect_aliasing` already documents.

`__init__` is exempt: it **creates** the field, so there is no prior region content for a
preservation property to be about. (Reopening condition: if PyCSL ever models an explicit
re-invocation of `__init__` on a live object, that carve-out must be re-measured.)

The new message names only conditions **the emitter actually checks** — "write through
`self.f[i]` so each index is checked" (clause (A) checks exactly that) and "add `<fn>` to
the `except` set" (checked by `fn.name in except_set`). Per gen #12's discriminator, that is
the safe shape; it names no marker that is merely *read*.

## CERTIFIED BOUNDARY RECORDED ALONGSIDE — the alias axis

`d = self.disk; d[1000] = v` in a non-exempt method is **not** guarded in the region-write
form either (the `reading` form rejects it explicitly; this form does not). Measured at
HEAD: it is **refused**, but by an **ill-typed emission** — `This expression has type
array.Array.array int @rho, but is expected to have type int` — i.e. the value model will
not bind a field array to a local at all.

**CORRECTED AFTER READING THE SPEC, AND THE CORRECTION MATTERS.** My first reading called
that a bare *type accident*, the #42 shape. **It is not — it is DOCUMENTED DESIGN.**
`docs/pycsl-static-semantics-reference.md` §2.5, under "Soundness (composition theorem)",
says: *"No alias analysis is needed (the obligation is at the location written;
**value-semantic arrays bar local-alias escape**)."* So the alias axis is defended on
purpose, by the value model's semantics, and the ill-typed emission is that defence showing
up at the command line — not an accident standing in for a missing guard. The distinction is
the difference between a CERTIFIED BOUNDARY *with a named defender* and an unmeasured hole,
and I had it wrong until I read the rule. **Before filing something as a type accident, check
whether a spec somewhere claims it on purpose.**

**REOPENING CONDITION (unchanged in substance, sharper in attribution): THE DEFENDER IS THE
VALUE MODEL, NOT THIS PASS.** The day the value model can bind a field array to a local — or
pass `self.f` as an array argument to a helper that stores into it — the confinement forms
lose their only defence on the alias axis, with nothing in `_weave_happy` to replace it, and
this becomes a live route. That is route #89's lesson exactly: **a fence owned by a DIFFERENT
subsystem can be un-armed by a completeness gain nobody thinks of as touching this gate.**
The repair is already written next door (the `reading` form's explicit alias rejection); it
was NOT copied in this increment because the case is currently unreachable, and an
unreachable guard cannot be negative-tested — which would make it precisely the kind of
unmeasured "fix" this campaign refuses to ship.

## THE SPEC SAID IT CORRECTLY AND THE CODE DID NOT — WHERE THE PREMISE IS WRITTEN DOWN

`docs/pycsl-static-semantics-reference.md` §2.5 states the composition theorem this way:

> *"If every body-verified method discharges a `#@ check φ(ℓ)` **at each write site of
> `self.f` (universal coverage, clause 1)** and every other mutator is exempt or carries the
> `\preserves` region-preservation `ensures` (clause 2), then no execution writes the
> protected region."*

**"UNIVERSAL COVERAGE" IS EXACTLY THE PREMISE #91 AND #92 FALSIFIED.** The theorem is stated
correctly and the specification is not at fault; the site collector simply was not universal —
it covered subscript point writes and nothing else. So this pair of routes is not a spec gap
but an **implementation that silently failed to meet a premise its own documentation sets in
bold**. That is worth internalising because it says where to look next:

>>> **WHEN A SOUNDNESS ARGUMENT NAMES A COVERAGE PREMISE ("every write site", "all paths",
>>> "each store"), GO AND COUNT THE CASES THE CODE ACTUALLY COVERS. THE PREMISE IS A CLAIM
>>> ABOUT A COLLECTOR, AND THE COLLECTOR IS THE THING NOBODY RE-READS.**

## GATES

* fidelity: `check-self-annotate-sync.sh` OK (887 functions); `self-annotate-mirror-check.sh`
  **byte-identical to HEAD** (the same 3 pre-existing `module6_whyml` drifts, rc=1 both
  sides — diffed, delta ZERO). `Module3_Weaver` does not appear in the drift set.
* corpus: witnesses **1247** (the exploit, `# pycsl-expected: FAIL` with its mechanism),
  **1248** (the `except` escape hatch still VERIFIES — the guard is not blanket; this is the
  control corpus 1057 taught the campaign to write), **1249** (an out-of-region write still
  PROVES — non-vacuity).
* the `\preserves` positive control **0461 still VERIFIES**; **0462** (the teeth test) and
  the 27 other `happy` corpus files are untouched — the three that rebind a field
  (0721, 0723, 0725) use `precond`/`postcond` forms that `continue` long before this branch.
* metric unmoved: markers **459** / grep 484 / offset 25 / unattached 0 — as expected, a
  refusal costs the trust surface nothing.
