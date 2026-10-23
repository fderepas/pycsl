# The `Dict[str, Any]` wall — the ceiling on self-TCB reduction

*Self-contained report, 2026-07-07. Branch `ghost-assign-bc6`, `\trusted` count 1240.*

## TL;DR

PyCSL verifies its own emitter: a mirror of `src/pycsl/` under `src/self-annotate/src/` where each
method is either **verified** (self-proven by PyCSL) or a **`\trusted` stub** (assumed correct). Driving
that trusted count down is the "self-TCB reduction" campaign. After converting the tractable stubs and
banking a certified value-ADT foundation, ~141 stubs remain trusted. **Almost all of them are blocked by
one wall: PyCSL cannot faithfully model a generic `Dict[str, Any]` in WhyML.** This is not a bug to fix
or a missing recognizer — it is a research-grade value-modeling problem, and it is **measured** (census +
a feasibility spike + two emission probes), not assumed. It is **not a soundness hole**: a trusted stub
is *assumed*, never *falsely proven*. This report explains exactly what the wall is, why the ADT we
already built does not reach it, the evidence, and what breaking it would actually cost.

---

## 1. What "the wall" is, in one sentence

The Module-6 emitter is a program that **reads Python IR as untyped dictionaries** (`Dict[str, Any]`)
— arbitrary string keys, values that may be an int, a string, a bool, a list, or another nested dict —
and PyCSL's WhyML target has **no faithful type for such a heterogeneous, dynamically-typed value**, so
every attempt to verify a method that reads one collapses the value to `int` and the proof fails on a
type mismatch (`this expression has type int, but is expected to have type string`).

## 2. Why this is the *dominant* residual (the numbers)

Of the ~141 still-trusted stubs, a whole-body census (`getting-better/tier3/whole-body-census.md`)
classified the blockers:

| class | ~count | blocker |
|---|--:|---|
| **V1** generic `Dict[str, Any]` readers | ~85 | the wall, directly |
| **V2** collection-result builders | ~43 | **~40 of 43 read `Dict[str, Any]` internally** — the wall behind a façade |
| **V3** emitter string / self-state / emission | ~13 | mixed; the genuine ones still hit the wall on re-port |

So the *effective* reach of this one wall is **~125 of 141**. It is the ceiling, not a corner case.

## 3. The four faces of the wall

The wall is a *class* of gap, not a single missing feature. A stub is blocked if it does **any** of:

1. **Heterogeneous value typing.** A `Dict[str, Any]` value, a `(str, int)` tuple, or a mixed list has
   no single element type. PyCSL defaults the element/value type to `int`, so any *string* slot
   mistypes. Example (real, from `_emit_metatype_tags`): `for nm, v in (("tag_int", 0), …)` — unpacking
   `(str, int)` pairs types **both** slots `int`, and the emitted WhyML does `int_to_string nm` on what
   is actually the string `"tag_int"`. Instant `int`/`string` failure.

2. **Generic reflection with no type to dispatch on.** The hard readers walk the dict *generically* —
   `for v in obj.values()`, reads by a computed/arbitrary key — rather than dispatching on a known tag.
   There is no discriminant to project against, so no ADT arm applies (see §4).

3. **By-reference container mutation.** Some walkers mutate a `Set[str]`/`Dict` parameter in place
   (`targets.add(x)`). This is an *aliasing/frame* boundary (the "WL-05" rejection class), **orthogonal
   to value typing** — a perfect value model would not fix it.

4. **String emission from dynamic values.** The emitter often turns the dynamic value into a WhyML
   *string* (it is a code generator). That couples value-reading with string-building, so even a modeled
   value must survive the string-emission path.

A stub converts only if it dodges **all four**. Most trip at least one.

## 4. Why the ADT we already built does **not** break this wall

The 2026-07 campaign built and certified an **IR-node value ADT** (`preamble.py::_emit_exprir_theory`,
`expressions.py` discriminant/projection, a Rocq/Lean record-valued certificate, 3-axiom ledger held —
`getting-better/tier3/`). It works — for the **typed-node** case: code that does
`node.get("type")` and then projects named fields (`BinOp` → `left`/`right`/`op`, etc.). There the node
*is* a `Dict[str, Any]`, but the code **dispatches on a known tag**, so the ADT can give it a typed arm.

The residual wall is the **opposite reflection style**: *generic* readers with **no tag to dispatch on**.
The ADT is addressed by kind; a `for v in obj.values()` walk over arbitrary keys has no kind to address.
This is the single most important distinction (SKILL §10.3): **the convertibility axis is reflection
*style*, not node kind.** Typed-node reads → ADT-addressable (done). Generic-`Any` walks → the wall.

## 5. The evidence — this is measured, not assumed

Three independent probes, all converging:

- **Census (option A):** ported each candidate's whole body, ran full `--fun` proof, reverted, classified.
  Result: **0 of 98 whole-body-convertible.** Ranked feature map showed the only high-fan-out lever is
  "faithful `Dict[str, Any]`," which is *not a bounded feature*.

- **F-B1 feasibility spike** (`getting-better/tier3/fb1-feasibility-spike.md`): built a candidate model
  — a pure heterogeneous value `type pyval = PInt int | PStr string | PBool bool | PNone | PList (list
  pyval) | PDict (list (string, pyval))`. The **type itself is fine**: it type-checks, terminates
  (structural `variant`), proves 14/14 read-back / dispatch / generic-walk laws on **both** Alt-Ergo and
  Z3 with **no new axiom**, and a Rocq/Lean certificate for it would be conservative and axiom-free. **But
  the decisive test — port a real generic-dict walker and whole-body-prove it — FAILED (NO-GO):**
  - `find_named_expr_targets(obj, targets)` → rejected at the emitter on **by-ref `Set` mutation** (face 3);
  - `find_return_type(stmts)` (read-only) → **`array int` vs `int`**, the opaque-dict collapse itself (face 1),
    plus SMT frictions (string-keyed dispatch times out under the recursive read; the pair-nested
    walk's termination VC won't discharge).
  Conclusion: **even a sound value type does not un-block the real walkers**, because they are also
  blocked by faces orthogonal to value typing.

- **Two emission-defect probes** (`getting-better/tier3/emission-defect-spike-findings.md`): both were
  *genuine* emitter bugs (a multi-`_` tuple-unpack emitting a duplicate WhyML variable; the `(str,int)`
  tuple mistyping above). Each has a real fix — but **self-verifying the fix requires re-proving a
  verified emitter method**, and three natural formulations of each re-port all failed on the **same
  `int`/`string` value-model gap.** The tool cannot yet self-verify its own bug-fixes. Honest clean
  yield of the emission lever: **0**.

Every path hits the same wall from a different angle. That convergence is the point.

## 6. What breaking the wall would actually cost

Not one feature — a **stack of coupled obligations**, each research-grade:

1. **A faithful generic-heterogeneous value model** (`pyval`) in WhyML — feasible in isolation (the spike
   proved the type + laws), but it is the "no-more-int" modeling change *at scale*: every dict read,
   `.values()` walk, and heterogeneous unpack must route through it.
2. **A co-landing formal-semantics certificate** that the new value shape is sound (the coupling rule,
   SKILL §10.5) — feasible and axiom-free, but must keep the 3-axiom ledger at 3.
3. **By-reference container-mutation modeling** (WL-05) — a *separate* aliasing/frame problem the value
   model does not touch, needed for the mutating walkers (face 3).
4. **Dynamic-value string-emission** — the value must survive being turned into WhyML text (face 4).
5. **SMT tractability** — even when types line up, the spike saw string-keyed dispatch and pair-nested
   termination VCs time out; these need trigger/measure engineering.

And the payoff is **low-ROI for the marker goal**: the fixed self-annotation contract is
`requires True / ensures True / assigns <frame>` (type-safety + frame, never value-faithful), so a
converted generic-dict reader adds **type-safety coverage, not behavioral content** — ~125 markers for a
multi-obligation research effort. High *soundness-story* value only if paired with the mechanized
Phase-7 value model in `src/formal-semantics/`; otherwise it is capability outrunning its certificate.

## 7. It is **not** a soundness hole

A `\trusted` stub is an **assumption**, not a false proof. Leaving the `Dict[str, Any]` readers trusted
means *that slice of the emitter is assumed correct in the self-verification rather than self-proven* —
it shrinks how much of the emitter PyCSL certifies about itself. It **never** lets a false program pass:
the wall bounds *coverage of the meta-verification*, not the soundness of what is verified. (Contrast a
real soundness hole — an added axiom, a vacuous contract — which the campaign gates specifically forbid.)

## 8. Bottom line

The remaining self-TCB frontier is a **semantic ceiling, not a backlog.** One wall — no faithful WhyML
model of a generic `Dict[str, Any]` — accounts for ~125 of 141 residual stubs, and it has four coupled
faces (heterogeneous typing, tagless generic reflection, by-ref mutation, string emission) that a single
value feature cannot all clear. This is proven by measurement (census 0/98, F-B1 NO-GO, emission lever 0),
so the value-first call to **leave these trusted and stop the marker campaign at 1240** is evidence-backed.
Breaking the wall is a legitimate future project — a faithful heterogeneous-value model **plus** its
certificate **plus** aliasing/frame modeling **plus** SMT engineering — undertaken for the *soundness
story* (jointly with formal-semantics Phase 7), **not** for marker count. Until then, the durable
deliverable stands: the certified IR-node ADT foundation, and a residual that is fully measured, not
assumed.

### Pointers
- Census & residual analysis: `getting-better/tier3/whole-body-census.md`, `…/step-d-leave-trusted-analysis.md`
- `Dict[str,Any]` model feasibility (NO-GO): `getting-better/tier3/fb1-feasibility-spike.md`
- Emission-defect probes: `getting-better/tier3/emission-defect-spike-findings.md`
- Plan of record & closure: `triage-ranked-tcb.md`; loop discipline: `config/skills/self-tcb-reduction/SKILL.md` (§10–§11)
