# opaque-and-refine.md — Specification opacity & data refinement for the os codec (umbrella for A/B/C/D)

**Date:** 2026-06-08 (rev. 2 — re-grounded on probe rounds 1–2)
**Status:** Global specification (context + concepts; A/B/C/D have their own detailed specs)
**Owner:** PyCSL tool ([TOOL], `src/pycsl/**`) + standard library ([STDLIB], `pure_lib/**`) +
formal-semantics ([FORMAL], `src/formal-semantics/**`).
**Origin:** the `try.md` retrospective (the inode round-trip is proven standalone but cannot be folded
into the os proof). **Re-grounded** by `challenging-the-plan.md` (round 1) and
`challenging-the-plan2.md` (round 2), which **replaced this document's cost/ordering estimates with run
probes.**

**Revision 2 — what the probes changed.** The *concepts* below (opacity, refinement, HAPPY) are
unchanged and correct. Their **cost and ordering moved**, decisively:
1. **"A now (cheapest)" was wrong — A reduces to B.** Probed: a round-trip `#@ lemma` proves only when
   `_pack_inode` carries its **rich** contract; with the light exported contract it **FAILS** (no
   field info to compose). The rich contract is exactly what rides the import stub — so only **opacity
   (B)** can hide it. **There is no cheap standalone A.**
2. **"C is just a refactor" was wrong — C needs two tool fixes.** Probed: the coupling invariant
   `ginode[n] == unpack(disk[slice])` did not compile (L0′ array-field-in-invariant gap → fixed), and
   even with **L0′ applied**, the *realistic* coupling that **calls `unpack_inode`** is **`unbound`** —
   a class invariant cannot reference a module function (emitted before functions exist). C needs a
   **second** fix (**L0″ — functions/logic-view in invariants**) *and then* an affordability re-test.
3. **The frame is NOT the wall (measured).** Inline coupling invariants now **compile and scale** —
   32 inodes (the os `MAX_INODES`) in **6s, linear** — so HAPPY's framing role is **confirmed
   affordable**. The wall is the **codec-in-the-invariant**, not the per-write frame.
4. **B is now the near-term route**, C the **highest-cost** (principled) target gated on L0′ (done) +
   L0″ + an affordability re-test. Sequencing in §7–§8 is rewritten accordingly.

---

## 1. The problem, precisely (wall #3)

`try.md` drove os 47 → 23 unproven and surfaced three walls. Two were crossed (tool gaps; the **SMT
array-state wall**, beaten by composing the proven leaf contracts — zero external proof). The third
blocks the codec round-trip from living in the os model:

> **Module-granularity / specification opacity.** `_pack_inode` is *imported* by `os/__init__` as a
> `val` stub carrying its **full** contract (1 length + 18 field ensures), called at **8 sites**. All
> 18 field-ensures propagate into all 8 syscall contexts (~144 heap-laden hypotheses); the syscalls
> prove *return codes* and do **not need** them, but must carry them, and the solver drowns (os does
> not complete in 1700s).

It is **not** soundness, **not** expressivity, **not** the array-state wall (already beaten). It is a
**proof-context-management** problem: *what rides the import stub into every caller.* `#@ no_inline`
does not help (it targets inlined methods, not imported free functions; the import propagates the
full contract; **there is no narrowed import**).

## 2. The core diagnosis: proving power ≠ proof-context management

> **An external proof, by itself, does NOT solve wall #3.** Proving the round-trip in Rocq/Lean and
> re-attaching it as a *rich contract on the os `_pack_inode` stub* bloats the 8 call sites **exactly
> as before** — the bloat is *what propagates*, not *how the fact was proved.*

What is missing is one (or both) of two classical mechanisms:

- **Opacity** (§4) — let clients import a *narrow* contract and `reveal` the rich one only where needed.
- **Refinement** (§5) — don't expose the 64-byte representation to clients at all; have them reason
  about an *abstract inode* and prove the representation refines it **once** at the boundary.

A proof assistant (track D) is valuable as the *opacity/durability layer* over one of these — never a
substitute (round-1 confirmed this by probe).

## 3. What the probes established (rounds 1–2) — the empirical core

This document is now grounded in run probes, not estimates:

| Premise (reasoned) | Probe result | Consequence |
|---|---|---|
| "A is the cheapest standalone route" | rich-contract lemma **proves**; **light**-contract lemma **FAILS** | **A reduces to B** — the lemma needs the rich contract, which is the bloat; only opacity hides it |
| "C is just a refactor" | coupling invariant **did not compile** (array field → unbound `subscript_get`) | needed **L0′** (now applied) before C's claim was even testable |
| "L0′ unblocks C" | inline couplings **compile and scale**: 8 inodes 3s, **32 inodes 6s, linear** | the **frame is affordable** — HAPPY's role confirmed cheap |
| (same) | the realistic coupling `ginode[n] == unpack_inode(disk[slice])` is **`unbound`** | a class invariant **cannot call a module function** — a **new wall** (L0″) distinct from L0′ |
| "inline the 18-field math instead" | untested | would re-introduce the **array-state cost** (wall #2) in the invariant × 32 inodes |

**Tool status:** **L0′** (array-field access in invariants/contracts → `Array.get`) is **applied and
gated** (os `formal_0001` 18/18; corpus 0 confirmed fails; fires only in spec context where the field
array type is known, so body reads and opaque cases are byte-identical). **L0″** (functions / a logic
view referenceable in a class invariant) is **not done** and is now **C's true gating prerequisite.**

## 4. Concept — Opacity (information hiding for specifications)

**Information hiding** (Parnas, 1972): expose an interface, hide the implementation. **Opacity is its
verification analogue:** a function has a **definition contract** (rich, verified inside its unit) and
an **interface contract** (narrow, what importers see), with the rich definition **hidden by default**
and *revealed* only in proofs that need it — simultaneously a **modularity** and a **proof-cost**
mechanism (the same act).

State of the art (mapped to Dafny in §9): **Dafny** `function {:opaque}` + `reveal`, and export sets
(`provides` vs `reveals`); **Coq/Rocq** `Qed`-opacity (clients see only the statement) + `Module Type`;
**F\*** `.fsti`/`.fst` + `--using_facts_from` (scope which facts reach the solver); **separation logic**
`open`/`close`.

**PyCSL's gap:** contracts are *all-or-nothing per function* and ride the import stub. **Track B**
(opaque-on-export + `#@ reveal`) closes exactly this — and per §3, **Track A's lemma route reduces to
B** (the lemma needs the rich contract that B must hide). B is therefore the *load-bearing* opacity
track, not an "if it recurs" afterthought.

## 5. Concept — Refinement (data refinement / the abstraction barrier)

**Data refinement** (Hoare, 1972): relate an **abstract value** to a **concrete representation** via an
**abstraction function** and a **coupling (representation) invariant**; reason at the abstract level,
discharge the coherence **once**. For the os codec (right on `_read_inode`/`_write_inode`):

```
_read_inode(n)      = _unpack_inode( disk[512+64n : +64] )
_write_inode(n, I)  = disk[512+64n : +64] := _pack_inode(I)
```

- **Abstract value:** inode = 18-field record (`ginode : int → inode_record`, ghost).
- **Concrete representation:** the 64-byte slice `disk[512+64n : +64]`.
- **Abstraction function:** `_unpack_inode`.
- **Coupling invariant:** `∀ n. ginode[n] == _unpack_inode(disk[512+64n : +64])`.
- **The one obligation:** `_write_inode(n, I)` re-establishes the invariant — the only place the
  round-trip is consumed; then syscalls reason about `ginode[n]` and never unfold the codec.

**What the probes (round 2) revealed about this shape — it is *not* free to express:**
- **L0′ (done):** array-field access *inside* an invariant (`disk[…]`) had to be taught to lower to
  `Array.get`. Until that fix the coupling invariant *did not compile*.
- **L0″ (not done — the new wall):** the coupling **calls `unpack_inode`**, and a class invariant
  **cannot reference a module function** (invariants are emitted in the type declaration, before
  functions exist) → **`unbound`**. C needs functions, or a **logic view of the codec**, usable in the
  invariant.
- **Affordability, conditional:** if the codec is exposed as a **logic view** (an *uninterpreted*
  `unpack_view`, with the round-trip stated as a lemma over it), the coupling `ginode[n] ==
  unpack_view(slice)` is a **cheap opaque equation** and the byte-math array-state cost is confined to
  the *one-time* round-trip lemma proof — *this is the affordable path*. If instead the 18-field byte
  math is **inlined** into the invariant × 32 inodes, it re-introduces the array-state wall. So C's
  affordability hinges on the logic-view codec, which is precisely what L0″ must enable.

Lineage: VDM, Z, the refinement calculus, Event-B; in automation, **Dafny**'s ghost-abstract-state
(`Valid()`) and **Creusot**'s `view` (`@`) — the same shape used for seq-promotion in
`07-1705-spec-rev4.md`. **Track C** is this — now known (by probe) to be the **highest-cost** track.

## 6. The role of HAPPY (region confinement) — and what the probes said about it

The coupling invariant must be **preserved by every write**: `_write_inode(n,…)` must show it left
inode `m ≠ n`'s slice untouched. That is the **region-confinement problem HAPPY solves** (`happy.md`):
a per-write `#@ check`, sound with no alias/call-graph analysis, 0 backend change. For inodes it is the
existing `region_integrity` HAPPY (region `[512,2560)`) plus a **parametric HAPPY** `inode_confinement(n)`
(`making-it-pure-5.md` §10) confining each write to `[512+64n,+64)`.

> **Round-2 measurement: the frame is affordable.** Inline coupling invariants with the per-write frame
> over **32 inodes prove in 6s, linearly.** So HAPPY's framing role is **confirmed cheap** — it is
> *not* the wall. The wall is the **codec-in-the-invariant** (§5, L0″), not the frame.

The three concepts still compose — but with the corrected cost:

```
HAPPY        frames the representation   — measured affordable (32 inodes, 6s)
Refinement   lifts to the abstract view  — blocked on L0″ (functions/logic-view in invariants)
Opacity      hides the codec             — Track B; the near-term route (A reduces to B)
```

## 7. The four tracks (corrected cost & ordering)

| Track | What it is | Concept | Cost (revised by probes) | Owner | Spec |
|---|---|---|---|---|---|
| **B** | **Opaque-on-export + `#@ reveal`** — interface (narrow, imported) + definition (rich, verified) contracts; `reveal` opts a caller in. **"Contract narrowing on import."** | Opacity (first-class) | **Medium — now the near-term route.** A depends on it; every imported codec hits the import bloat. | [TOOL] | `B-spec.md` |
| **A** | **Round-trip `#@ lemma` + `#@ uses`.** | Opacity (by hand) | **Reduces to B** (probed): the lemma needs the rich contract B must hide. Useful for cross-function *relations*, but **not a cheap standalone route.** | [STDLIB] + [TOOL] | `A-spec.md` (read with §3) |
| **C** | **Data refinement / abstract inode view** + HAPPY confinement. | Refinement + HAPPY | **Highest.** Needs **L0′ (done) → L0″ (functions/logic-view in invariants) → affordability re-test** at the real coupling (logic-view ⇒ likely affordable; inlined byte-math ⇒ array-state wall). | [STDLIB] + [TOOL] | `C-spec.md` |
| **D** | **Rocq/Lean bridge** — kernel-checked, solver-independent round-trip, exposed as an opaque lemma. | Opacity + durability | Medium. **Layer over A/C, never a substitute** (does not touch the bloat). | [TOOL] + [FORMAL] | `D-spec.md` |

## 8. Sequencing & recommendation (revised)

Round 1 corrected "A cheapest → A is B" and "C is a refactor → C needs L0′." Round 2 adds "L0′ is not
enough for C — it needs L0″, pushing C's cost up." The resulting order:

1. **L0′ [TOOL] — DONE.** Array-field access in invariants/contracts → `Array.get`. Gated (corpus
   clean, formal 18/18). Independently valuable: any class invariant over an array field now works.
2. **B [TOOL] — the near-term route to the goal.** Opacity / contract-narrowing-on-import keeps os
   light while the round-trip is established (in B's revealed definition, or a cited lemma) — and it is
   the prerequisite A turned out to need. **This is the most realistic path to "os stays at 23 and the
   round-trip is connected."**
3. **L0″ [TOOL] — C's true gating prerequisite.** Let a class invariant reference module functions / a
   **logic view** of the codec. Medium (emission-ordering, or a logic-view codec). Without it the
   realistic refinement coupling does not compile.
4. **C affordability re-test — only after L0″.** Test `ginode[n] == unpack_view(disk[slice])` × 32
   inodes with the codec as a **logic view**. If cheap (likely — opaque equation), C is viable but
   still the highest-cost track (logic-view codec + HAPPY + the ghost-state refactor). If it blows up,
   C is parked behind B.
5. **D [TOOL+FORMAL] — durability layer** over B (or C), when a kernel-checked, solver-independent
   round-trip is wanted. Never substitutes for B/C.

**Net:** **B is now the recommended near-term route**; A is subsumed by B; C is the highest-cost
principled target gated on L0′ (done) + L0″ + affordability; D hardens whatever proves the round-trip.

## 9. Comparison with Dafny (the closest analogue)

Dafny built precisely these mechanisms and treats opacity as a **proof-cost** tool — exactly PyCSL's
1700s symptom.

| PyCSL need / track | Dafny mechanism | Note |
|---|---|---|
| Narrow what a caller sees (B; A's manual form) | `function {:opaque} f` + `reveal f();` | hide body+rich post by default |
| Contract narrowing on import (B) | export sets: `export E provides f reveals g` | `provides` = signature; B's interface is a *custom* narrow contract (more expressive) |
| Control solver unfolding | `{:fuel f,0,0}` | the explicit anti-blow-up knob |
| Abstract inode view (C) | concrete field + `ghost var Contents` + `predicate Valid()` (coupling invariant), `requires/ensures Valid()` | the `Valid()` pattern *is* §5 |
| Functions usable in the invariant (L0″) | a Dafny `function` (logic) referenced in `Valid()` | Dafny invariants freely call logic functions; **PyCSL cannot yet** — this is L0″ |
| Frame which state a write touches (§6) | dynamic frames `reads`/`modifies` | PyCSL frames via **HAPPY** (per-site `check`), measured affordable to 32 inodes |
| Codec round-trip as a reusable fact (A/D) | `lemma` (inert until invoked) | A's form; reduces to B for the bloat |

Two differences: (1) PyCSL frames via **HAPPY**, not `modifies`; (2) Dafny designed opacity in *as a
performance feature* and lets invariants call logic functions — **two things PyCSL is still building**
(B = opacity; L0″ = functions-in-invariants). The Dafny lesson — *opacity is a proof-cost mechanism* —
is this document's thesis, now confirmed by the 1700s blow-up *and* the probe series.

## 10. Soundness invariants across all four tracks

1. **The round-trip is established, not assumed.** A/B/C consume the *proven* property (the
   leaf-compositional round-trip, drivers 0657/0658, or its refinement obligation); D adds the
   proof-assistant kernel + the Python→Lean translation to the **TCB** *only if it axiomatizes* (a
   ledger entry); *if it replays*, it does not.
2. **os return-code proofs are unaffected** — the point of every track is that the codec's field values
   stop riding into syscall contexts that only prove return codes.
3. **Fail-safe.** A wrong *narrowing* (B: an interface claiming more than the definition proves) fails
   the narrowing VC, fail-loud; a broken *coupling invariant* (C) fails the method's own proof; a
   tool prerequisite that is unmet (L0″) leaves the module **unchanged** — never a wrong proof in a
   client. (The anti-`\trusted` invariant, applied to opacity and refinement.)
4. **Byte-identical corpus** for files that touch none of this; os holds at its current count (23) or
   improves, never regresses. (L0′ already gated this way.)

## 11. The through-line (both probe rounds) — reason to design, probe to decide

Every step, a *reasoned* premise was overturned by a *run* probe:
- "external proof solves the bloat" → no (it's about what propagates). [`try.md`]
- "A is cheapest" → no, **A reduces to B**. [round 1]
- "C is a refactor" → no, **C needs L0′** to even compile. [round 1]
- "L0′ unblocks C" → partly: **inline couplings scale (32 inodes, 6s)**, but the realistic
  function-call coupling is **`unbound`** — C needs **L0″** too. [round 2]

The *concepts* (opacity, refinement, HAPPY) held throughout; their **cost and ordering** kept moving as
probes replaced estimates. **The discipline: reason to design the probe, run the probe to decide the
plan.**

## 12. Glossary

- **Opacity** — hiding a function's rich definition contract by default; clients import a narrow
  *interface* and `reveal` the definition where needed.
- **Interface vs definition contract** — the narrow contract importers see vs the rich contract
  verified in the owning unit.
- **Refinement / data refinement** — relating an abstract value to a concrete representation via an
  abstraction function and a coupling invariant; reasoning abstractly, proving coherence once.
- **Abstraction function / logic view** — the (ideally *uninterpreted* logic) map from representation
  to abstract value (here `_unpack_inode` / an `unpack_view`); a logic view keeps the coupling
  invariant a cheap opaque equation.
- **Coupling / representation invariant** — `∀n. ginode[n] == unpack(disk[slice])`.
- **HAPPY** — a whole-program confinement property expanding to per-write `#@ check`; no
  alias/call-graph analysis, 0 backend change; **measured affordable** to 32 inodes (§6).
- **L0′** — the (applied) fix: array-field access in invariants/contracts lowers to `Array.get`.
- **L0″** — the (open) fix: a class invariant may reference module functions / a logic-view codec.
- **`reveal` / fuel / lemma function** — opting a proof into a hidden definition / unfolding control /
  a separately-proven fact inert until cited.

## 13. References

**Information hiding & opacity**
- D. L. Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules," *CACM* 15(12), 1972.
- K. R. M. Leino, "Dafny: An Automatic Program Verifier for Functional Correctness," *LPAR* 2010
  (opaque functions, `reveal`, fuel, ghost state; export sets in the Dafny Reference Manual).
- N. Swamy et al., "Dependent Types and Multi-Monadic Effects in F\*," *POPL* 2016 (interface files;
  `--using_facts_from`, `friend` in the F\* manual).
- Y. Bertot, P. Castéran, *Coq'Art*, Springer 2004 (`Qed` opacity; `Module Type`).
- B. Jacobs, J. Smans, F. Piessens, "A Quick Tour of the VeriFast Program Verifier," *APLAS* 2010
  (predicate `open`/`close`).

**Refinement & data refinement**
- C. A. R. Hoare, "Proof of correctness of data representations," *Acta Informatica* 1(4), 1972.
- C. B. Jones, *Systematic Software Development Using VDM*, 2nd ed., 1990; J. M. Spivey, *The Z
  Notation*, 2nd ed., 1992.
- R.-J. Back, J. von Wright, *Refinement Calculus*, Springer 1998; C. Morgan, *Programming from
  Specifications*, 2nd ed., 1994; W.-P. de Roever, K. Engelhardt, *Data Refinement*, Cambridge 1998.
- J.-R. Abrial, *Modeling in Event-B*, Cambridge 2010.
- X. Denis, J.-H. Jourdan, C. Marché, "Creusot: a Foundry for the Deductive Verification of Rust
  Programs," *ICFEM* 2022 (the `view`/`@` model); Y. Matsushita et al., "RustHorn," *ESOP* 2020.

**Why3 (the backend) & proof-assistant bridging**
- J.-C. Filliâtre, A. Paskevich, "Why3 — Where Programs Meet Provers," *ESOP* 2013 (module cloning/
  refinement; Coq/Isabelle/PVS *realizations*).

**SMT instantiation / large-array blow-up (wall #2 & the C affordability risk)**
- L. de Moura, N. Bjørner, "Efficient E-matching for SMT Solvers," *CADE* 2007.

**HAPPY / MetAcsl origin (§6)**
- V. Robles, N. Kosmatov, V. Prevosto, L. Rilling, P. Le Gall, "MetAcsl: Specification and
  Verification of High-Level Properties," *TACAS* 2019.

**Project-internal**
- `try.md` — the round-trip retrospective (the three walls; §3.7–3.8 the module-granularity wall).
- `challenging-the-plan.md` / `challenging-the-plan2.md` — probe rounds 1 & 2 (the source of this
  revision's cost/ordering).
- `happy.md`, `making-it-pure*.md` (esp. `making-it-pure-5.md` §9 fine probe, §10 parametric HAPPY).
- `A-spec.md`, `B-spec.md`, `C-spec.md` (and `D-spec.md`) — the per-track details.
- `docs/pycsl-static-semantics-reference.md` — τ universe, RT/purity, module-import semantics.

> **In one line (rev. 2):** the inode round-trip is proven but cannot live in the os module because its
> rich contract rides the import stub into 8 syscall proofs that don't need it — a *specification-
> opacity / proof-context* problem, not a soundness/expressivity/SMT one. The fixes are **opacity**
> (narrow the exported contract, reveal on demand) and **refinement** (reason over an abstract inode,
> prove the codec refines it once, HAPPY confining each write). Probes then re-ordered the plan: **A
> reduces to B**; **C needs L0′ (done) + L0″ (functions/logic-view in invariants) + an affordability
> re-test** and is the **highest-cost** track (the *frame* is affordable — 32 inodes, 6s — but the
> *codec-in-the-invariant* is the wall); so **B (opacity) is the near-term route**, with D as the
> durable layer over B or C. Reason to design the probe; run the probe to decide the plan.
