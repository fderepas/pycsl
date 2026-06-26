# C-spec-rev2.md — Track C: data refinement via an abstract inode view (+ HAPPY confinement)

**Date:** 2026-06-08 (rev. 2 — re-grounded on probe rounds 1–2)
**Status:** Spec (for review — no code changed)
**Owner:** [STDLIB] (`pure_lib/**`, the model refactor) + [TOOL] (`src/pycsl/**`, L0″ + parametric HAPPY)
**Origin:** `opaque-and-refine.md` (rev. 2) §5–§6, §7–§8; `try.md` §3.7, §7; Hoare 1972. **Re-grounded**
by `challenging-the-plan.md`/`challenging-the-plan2.md`, which **probed C directly**.
**Concept:** **data refinement + HAPPY confinement** — reason over an abstract inode; prove the
representation refines it once; confine each write so the coupling invariant stays affordable.
**Relationship:** the **highest-cost** track and the **eventual structural answer** — *not* near-term.
**B ships sooner** (umbrella rev. 2 §8); C is gated on **L0′ (done) → L0″ (open) → an affordability
re-test**, and it **consumes** the round-trip from A/B/D and opacity (of a logic-view codec).

**Revision 2 — what the probes changed for C.**
1. **The round-1 blocker is fixed.** `ginode[n] == unpack(disk[slice])` failed to compile (array field
   → unbound `subscript_get`); **L0′ is now applied** (gated: os `formal_0001` 18/18, corpus clean), so
   array-field access in invariants lowers to `Array.get`. Expressibility of the *frame* part: solved.
2. **The frame is affordable — measured.** Inline coupling invariants now compile and **scale: 8
   inodes 3s, 32 inodes (`MAX_INODES`) 6s, linear.** HAPPY's framing role is **confirmed cheap** — it
   is *not* the wall (§6).
3. **The realistic coupling is `unbound` — a new wall (L0″).** The real coupling **calls** `unpack_inode`,
   and a class invariant **cannot reference a module function** (invariants emit in the type
   declaration, before functions exist) → `unbound`. C needs **L0″** — functions / a **logic view** of
   the codec usable in invariants (§7, §8). This is now C's **true gating prerequisite**, not the
   refactor.
4. **The affordable path is a logic-view codec (= opacity of a logic function).** §8: an *opaque* logic
   `unpack_view` makes the coupling a **cheap opaque equation** and confines the byte-math array-state
   cost to the *one-time* round-trip lemma. Inlining the 18-field byte math instead re-introduces the
   array-state wall × 32 inodes. So C is **not** independent of opacity.
5. **C is the highest-cost track.** L0′ (done) + L0″ + logic-view machinery + the ghost-state refactor +
   the round-trip (A/B/D). **B is the near-term route**; C is the structural endpoint.

---

## 1. Goal & non-goal

**Goal.** Dissolve wall #3 **structurally**: give the syscalls an **abstract inode view** (ghost
`ginode : int → 18-field record`); maintain the **coupling invariant** `ginode[n] ==
unpack_view(disk[512+64n:+64])` **once** at the codec boundary; so syscalls reason about `ginode[n]`
and **never unfold the codec** — the 18 field-ensures cannot bloat them. Beyond wall #3, C yields a
clean model for **rich** inode properties (type, link_count, size).

**Non-goal.** B/A's keep-the-codec-revealable approach (C hides it entirely — but, per §8, *uses*
opacity internally for the logic view); the *near-term* unblock (that is B — umbrella rev. 2 §8);
the 23 return-code goals (`08-1537`); building L0″ or parametric HAPPY themselves (consumed here,
specced in the report / `making-it-pure-5.md` §10).

## 2. The data-refinement structure (Hoare, 1972)

On the existing boundary:
```
_read_inode(n)      = _unpack_inode( disk[512+64n : +64] )
_write_inode(n, I)  = disk[512+64n : +64] := _pack_inode(I)
```

| Refinement element | In the os model |
|---|---|
| **Abstract value** | inode = 18-field record, `ginode : map int (array int)` (ghost) |
| **Concrete representation** | the 64-byte slice `disk[512+64n : +64]` |
| **Abstraction function** | `_unpack_inode` — exposed as a **logic view** `unpack_view` (§8) |
| **Coupling invariant** | `∀ n. ginode[n] == unpack_view(disk[512+64n : +64])` |
| **The one obligation** | `_write_inode(n, I)` re-establishes it — the only place the round-trip is consumed |

## 3. What the probes established about C (the empirical core)

| C dimension | Round-2 result |
|---|---|
| Array-field access in an invariant (round-1 blocker) | ✅ **fixed by L0′** (applied, gated) |
| Inline coupling, frame over many inodes (round-1 affordability worry) | ✅ **affordable** — 32 inodes, 6s, linear |
| Realistic coupling `ginode[n] == unpack_inode(slice)` (function call in invariant) | ⛔ **`unbound`** — needs **L0″** (§7) |
| Inline alternative (18-field byte math in the invariant × 32) | ⚠️ untested; would hit the **array-state wall** (§8 explains the logic-view fix) |

The frame is solved and cheap; the **codec-in-the-invariant** is the wall, and the **logic-view codec**
(§8) is the affordable resolution.

## 4. The boundary operations — where the codec is consumed, once

**`_write_inode(n, I)`** — concrete `disk[slice] := _pack_inode(I)`; abstract `ginode[n] := I`.
- **Re-establish coupling for `n`:** `ginode[n] (=I) == unpack_view(disk[slice] (=pack(I))) ==
  unpack_view(pack_view(I)) == I` — **by the round-trip lemma over the logic views** (from A/B/D, §8). A
  **lemma citation, not byte math.** *The sole consumption of the round-trip in the whole model.*
- **Preserve coupling for `m ≠ n`:** `ginode[m]` and `disk[512+64m:+64]` unchanged — **by HAPPY
  confinement** of the write to `[512+64n,+64)` (§6).

**`_read_inode(n)`** — returns `ginode[n]`; by the coupling invariant `_read_inode(n) == ginode[n]`, so
**read-back is free** (no per-call round-trip).

> `_pack_inode`/`_unpack_inode` and their logic views appear **only** in `_write_inode`, `_read_inode`,
> and the coupling invariant — nowhere else.

## 5. Syscalls reason abstractly (the barrier)

A syscall reads/writes `ginode[n]` *fields* and never unpacks bytes:
```python
#@ ensures \result == 0 ==> ginode[n].type == 2     # a directory-typed inode  (illustrative)
def sys_mkdir(self, path, mode): ...
```
The 18 field-ensures **never enter a syscall's proof context** — there is no rich contract on
`_pack_inode` to propagate. **Wall #3 dissolved structurally** (A keeps the round-trip in a lemma; B
keeps it on the function hidden-but-revealable; **C removes it from the syscalls' world**).

## 6. The role of HAPPY (the framing) — measured affordable

The coupling invariant must be **preserved by every write**: `_write_inode(n,…)` must show inode
`m ≠ n`'s slice is untouched. That is the **region-confinement HAPPY** (`happy.md`) — existing
`region_integrity` (region `[512,2560)`) plus a **parametric HAPPY** `inode_confinement(n)`
(`making-it-pure-5.md` §10) confining each write to `[512+64n,+64)`.

> **Round-2 measurement: the frame is affordable.** Inline coupling invariants with the per-write frame
> over **32 inodes prove in 6s, linearly.** HAPPY's framing role is **confirmed cheap** — *not* the wall.

(The §6 frame measurement used the *inline* 2-byte coupling; with the logic-view codec (§8) the coupling
is an opaque equation, so the frame re-confirmation at the realistic shape rides on top of L0″.)

## 7. The two tool prerequisites (L0′ done, L0″ the new gate)

| Prereq | What | Status |
|---|---|---|
| **L0′** | array-field access in invariants/contracts → `Array.get` (the round-1 blocker) | ✅ **done** (gated; independently valuable — any class invariant over an array field now works) |
| **L0″** | a class invariant may reference **functions / a logic view** of the codec (`unpack_view`); i.e. declare logic functions before the type decls, or expose a logic-view codec usable in invariants | ⛔ **open — C's true gating prerequisite** |

Without L0″ the realistic refinement coupling **does not compile** (round-2 `unbound`). L0″ is medium
(emission-ordering, or — better — a logic-view codec with opacity, §8).

## 8. The logic-view codec — the affordability answer (and why C depends on opacity)

The realistic coupling fails two ways (§3): as written `_unpack_inode` is **unbound** in an invariant;
inlined, the 18-field byte math re-hits the **array-state wall** × 32 inodes. The resolution is a
**logic view** — and it is itself **opacity applied to a logic function**:

- Define a **logic function** `unpack_view : array int → array int` (the abstraction function, as
  logic), with a bridge lemma `∀d. _unpack_inode(d) == unpack_view(d)` (the program function returns the
  logic value); symmetrically `pack_view`.
- The coupling invariant references the **logic** view: `ginode[n] == unpack_view(disk[slice])` —
  referenceable (that is what **L0″** enables) and **cheap**, because `unpack_view` is kept **opaque**
  (body not unfolded by the solver): the coupling is one **opaque equation** per inode, **not** byte
  math. This is exactly the inline-equation shape that scaled to 32 inodes in 6s (§6).
- `_write_inode(n,I)` re-establishes the coupling by **citing the round-trip lemma over the logic
  views** (`∀x. unpack_view(pack_view(x)) == x`) — a lemma citation (§4), not a re-derivation.
- **The byte-math array-state cost is unfolded exactly once** — inside the round-trip lemma's own proof,
  where the views are revealed. Everywhere else the views stay opaque and the coupling stays cheap.

> **C's affordable path is opacity-of-a-logic-function** — the same concept as Track B (hide the rich
> definition; reveal once), applied to the logic-view codec rather than a program contract. So C is
> **not** independent of opacity, and until L0″ ships the logic-view-in-invariants capability, C's
> central affordability claim **cannot even be tested** (the function-call coupling is `unbound`).

## 9. Dependencies — C is an integration point

| Needs | From | Used where |
|---|---|---|
| **L0′** (array fields in invariants) | [TOOL] | the coupling invariant's `disk[slice]` — **done** |
| **L0″** (functions/logic-view in invariants) | [TOOL] | referencing `unpack_view` in the invariant — **open, the gate** |
| **logic-view codec** (`unpack_view`/`pack_view` + bridge lemmas, opaque) | [STDLIB]+[TOOL] | the cheap coupling (§8) |
| the **round-trip lemma** (logic-view form) `unpack_view(pack_view x)=x` | **A** / **B** (revealed) / **D** (kernel) | consumed **once** in `_write_inode` (§4) |
| **parametric HAPPY** `inode_confinement(n)` (or narrow-slice `assigns`) | `making-it-pure-5.md` §10 | preserving coupling for `m≠n` (§6) |
| **ghost-state machinery** (ghost map + class invariant carried through methods) | [TOOL]/existing | the coupling invariant (§2) |

C does **not** stand alone; it composes opacity (§8), the round-trip (A/B/D), and confinement.

## 10. Comparison with Dafny / Creusot

| C | Dafny | Creusot |
|---|---|---|
| `ginode` (ghost) | `ghost var Contents` | the `@`/`view` |
| coupling invariant | `predicate Valid()` | the view relation |
| methods maintain it | `requires/ensures Valid()` | view contracts |
| **`unpack_view` referenced in the invariant (L0″)** | a Dafny **`function` freely called in `Valid()`** | a logical `view` function |
| framing | `reads`/`modifies` | borrow/ownership; **C uses HAPPY** |

Two gaps the probes named: Dafny invariants **freely call logic functions** (that is **L0″**, which
PyCSL lacks), and Dafny ships opacity (`{:opaque}`) as a performance feature — **two things PyCSL is
still building** (L0″; opacity = the §8 logic-view + Track B). Foundational: Hoare 1972; `Valid()` is
Dafny's realization, `view` is Creusot's (the same shape as `07-1705-spec-rev4.md`'s seq view).

## 11. Soundness & fail-safe

- **The round-trip is proven** (A/B/D), **consumed not assumed** (§4) — no new trust.
- **The logic view is bridged to the program codec** (`∀d. _unpack_inode(d)==unpack_view(d)`), so the
  coupling invariant is **meaningful** (ginode[n] equals the *actual* unpacked inode), not an arbitrary
  uninterpreted function — opacity hides the *body*, never changes the *value*.
- **The coupling invariant is a class invariant** — re-proven at every method exit; pervasive but sound
  (the cost, §13a).
- **HAPPY confinement is sound** (per-site coverage, 0 backend change).
- **No TCB growth** (the only TCB question is D-if-axiomatized, ledgered where D is used).
- **Fail-safe.** A method that cannot re-establish the coupling (round-trip unavailable, or HAPPY can't
  confine) **fails loud**; a broken bridge lemma fails its **own** proof; an unmet prerequisite (L0″)
  leaves the model **unchanged** until the fix lands (status quo, no regression).

## 12. Feasibility gate (the original probe has been *run*; here is what remains)

Round-2 ran the original §-probe: inline couplings **scale** (32 inodes, 6s) ✅; the function-call
coupling is **`unbound`** ⛔. So the remaining gate is **after L0″**:

> Re-test `ginode[n] == unpack_view(disk[slice])` × 32 inodes with `unpack_view` **opaque** (§8).
> **Pass** (cheap opaque equation, as §6 suggests) ⟹ C is viable (still the highest-cost track).
> **Fail** ⟹ C is parked behind B until the cost is understood.

## 13. The genuinely hard parts (stated plainly)

a. **Cost — highest of the four tracks.** L0′ (done) + **L0″** (open) + the **logic-view codec**
   (functions + bridge lemmas + opacity) + the **pervasive refactor** (ghost `ginode` threaded
   everywhere; coupling invariant re-proven at every disk-writing method's exit; syscalls **rewritten**
   to abstract reads/writes) + the **round-trip** (A/B/D). Do not undersell it.
b. **L0″ is a confirmed prerequisite, not a "maybe."** Round-2 proved the realistic coupling is
   `unbound` without it — C **cannot compile**, let alone be affordability-tested, until L0″ ships.
c. **Worth-it threshold — be honest.** For the round-trip alone, **B is the near-term route** and C is
   over-engineering. C **earns its cost** only when the os model must prove **rich** inode properties
   (`sys_mkdir ⟹ type==2`, `sys_link ⟹ link_count+1`, `sys_truncate ⟹ size`) — which want the abstract
   inode view. Adopt C for that; until then, B.

## 14. Phasing

| Phase | Delivers | Gate | Owner |
|---|---|---|---|
| **P-1** | **L0′** — array-field access in invariants → `Array.get` | **DONE** (corpus clean, formal 18/18) | [TOOL] |
| **P0** | the feasibility probe (§12) — **run**: inline scales (32 inodes 6s) ✅, function-call `unbound` ⛔ | **DONE finding**: L0″ required | [TOOL]+[STDLIB] |
| **P1** | **L0″** — logic functions / a logic-view codec referenceable in class invariants, with **opacity** so `unpack_view` can be opaque (§7, §8) | **[PROVE]** a class invariant referencing an opaque logic function compiles & is cheap | [TOOL] |
| **P2** | the **logic-view codec**: `unpack_view`/`pack_view` + bridge lemmas; the **round-trip lemma over the logic views** (consuming A/B/D); the §12 affordability re-test (coupling × 32 inodes, opaque views) | **[PROVE]** bridge lemmas + round-trip; **[measure]** coupling cheap at 32 inodes | [STDLIB]+[TOOL] |
| **P3** *(if needed)* | **parametric HAPPY** `inode_confinement(n)` (or narrow-slice `assigns` + disjointness) for the realistic-shape frame | per-site checks discharge; frame re-confirmed cheap on the logic-view coupling | [TOOL] |
| **P4** | ghost `ginode` + coupling class invariant (logic-view form); initialize in the constructor; prove `_write_inode`/`_read_inode` maintain it (cite the round-trip lemma) | **[PROVE]** coupling holds after each; round-trip consumed **once** | [STDLIB] |
| **P5** | rewrite **one** syscall (`sys_mkdir`) to reason over `ginode[n]` fields, **without** unfolding the codec | **[PROVE]** the syscall; **[measure]** 0 field-ensures, views opaque | [STDLIB] |
| **P6** | migrate remaining inode-touching syscalls; rich inode properties as the payoff; corpus sweep | **[PROVE]** a rich property (`sys_mkdir ⟹ ginode[n].type==2`); os coverage improves; corpus PASS | [STDLIB] |

P1 (L0″) is the gate; P2 builds the affordable logic-view codec and re-tests affordability; P4 lays the
coupling boundary; P5 proves the barrier on one syscall; P6 is the payoff that justifies C's cost.

## 15. Acceptance criteria

1. **L0″**: a class invariant referencing an **opaque logic function** compiles and the coupling is
   **cheap** (× 32 inodes, comparable to the §6 inline result) — **[PROVE / measure]**.
2. `ginode` + the **logic-view coupling invariant** are established and maintained by
   `_write_inode`/`_read_inode` — **[PROVE]**.
3. A syscall (`sys_mkdir`) proves **without unfolding the codec**; **0 field-ensures** and **opaque
   views** in its context — **[PROVE / measure]**.
4. **Read-back is free** from the coupling invariant — no per-call round-trip — **[PROVE]**.
5. The round-trip lemma is consumed **exactly once** (in `_write_inode`) — **[inspect]**.
6. The bridge lemma `∀d. _unpack_inode(d)==unpack_view(d)` holds, so the coupling is **meaningful**;
   a deliberately-broken coupling re-establishment **fails the method's own proof** — **[PROVE / PROVE-neg]**.
7. A **rich inode property** (`sys_mkdir ⟹ ginode[n].type == 2`) becomes statable and provable —
   **[PROVE]** — the payoff beyond wall #3 (§13c).

## 16. Relationship to A / B / D

- **B — the near-term route; C the structural endpoint** (umbrella rev. 2 §8). B keeps the codec
  *revealable* and ships sooner; C hides it below a barrier (but uses opacity internally for the logic
  view, §8) and costs L0″ + a refactor. **Do B now; do C when rich inode reasoning is the goal.**
- **A — reduces to B** (probed); A's lemma route is subsumed by opacity. C consumes the **round-trip
  lemma** that A/B/D establish (in logic-view form, §8), once.
- **D — durability layer.** D's kernel-checked round-trip can back C's logic-view round-trip lemma
  (solver-independence); the logic-view surface is unchanged.
- **C consumes parametric HAPPY** (`making-it-pure-5.md` §10) and **L0″** (this report) — both specced
  elsewhere.

## 17. Out of scope

A/B's lemma/reveal routes as the *primary* mechanism (C is the alternative philosophy, though it uses
opacity for §8); D's Rocq/Lean realization; the L0″ tool fix and parametric-HAPPY mechanism *themselves*
(consumed here); the `#@ no_inline` return-code work (`08-1537`); direntry abstraction (same pattern,
fold in after the inode view); a record-typed abstract inode (a clean refinement of the 18-field-list
`ginode`, deferred).

> **In one line (rev. 2):** C dissolves wall #3 at the root by **data refinement** — a ghost abstract
> inode `ginode` with a coupling invariant `ginode[n] == unpack_view(disk[slice])` maintained **once**
> at `_write_inode` (citing the round-trip from A/B/D) and **preserved** by HAPPY confinement — but the
> round-2 probes showed it is the **highest-cost** track: L0′ is done and the **frame is affordable (32
> inodes, 6s)**, yet the realistic coupling that calls `unpack_inode` is **`unbound`** in a class
> invariant, so C needs **L0″** plus a **logic-view codec** (an *opaque* `unpack_view` — opacity applied
> to a logic function — which makes the coupling a cheap opaque equation and confines the byte-math to
> the one-time round-trip lemma); since **B is the near-term route**, C is the eventual structural
> endpoint, gated on L0″ → an affordability re-test, and justified when the os model needs **rich**
> inode reasoning rather than the round-trip alone.
