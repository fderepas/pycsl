# opaque-and-refine.md — Specification opacity & data refinement for the os codec (umbrella for A/B/C/D)

**Date:** 2026-06-08
**Status:** Global specification (context + concepts; A/B/C/D get their own detailed specs)
**Owner:** PyCSL tool ([TOOL], `src/pycsl/**`) + standard library ([STDLIB], `pure_lib/**`) +
formal-semantics ([FORMAL], `src/formal-semantics/**`) — per-track ownership in §6.
**Origin:** the `try.md` retrospective — the inode round-trip `_unpack_inode(_pack_inode(x))[k] ==
x[k]` is **proven standalone** (drivers 0657/0658) but **cannot be folded into the whole-os proof**
(os does not complete in 1700s). This document explains *why* that is, names the two concepts that
solve it (**opacity**, **refinement**), gives **HAPPY** its role, compares with **Dafny**, and frames
the four solution tracks. It changes no code.

---

## 1. The problem, precisely (wall #3)

`try.md` drove os from 47 → 23 unproven and surfaced three independent walls. Two were crossed:
tool gaps (transpiler fixes) and the **SMT array-state wall** (proving byte arithmetic over a
64-element array times out — crossed by *composing* the already-proven leaf contracts, zero external
proof). The third blocks the codec round-trip from living in the os model:

> **Module-granularity / specification opacity.** `_pack_inode` is *imported* by `os/__init__` as a
> `val` stub carrying its **full** contract (1 length + 18 field ensures), and it is **called at 8
> sites**. So all 18 field-ensures propagate into all 8 syscall proof contexts (~144 heap-laden
> hypotheses). The syscalls prove *return codes* and do **not need** the field values — but must carry
> them, and the solver drowns.

The decisive facts (from `try.md` §3.7–3.8):

- This is **not** a soundness problem — the contract is correct.
- This is **not** an expressivity problem — the round-trip is provable (0657/0658).
- This is **not** the SMT array-state wall — that was already beaten by composition.
- It is a **proof-context-management** problem: *what rides the import stub into every caller.*
- `#@ no_inline` does **not** help — it targets inlined methods on module-global instances; an
  imported free function is *already* a modular `val`, and the import propagates the **full** contract.
  There is **no mechanism to import a narrowed contract.**

## 2. The core diagnosis: proving power ≠ proof-context management

The instinct to "prove an abstraction in Rocq/Lean and bridge the gap" is **half right, and the
valuable half is not the proving.** The round-trip is already proven by composition; a kernel proof
adds *durability*, not capability. Crucially:

> **An external proof, by itself, does NOT solve wall #3.** If the round-trip is proven in Lean and
> re-attached as a *rich contract on the os `_pack_inode` stub*, the 8 call sites bloat **exactly as
> before** — because the bloat is *what propagates to call sites*, not *how the fact was established*.

What is actually missing is one (or both) of two classical mechanisms:

- **Opacity** (§3) — let clients import a *narrow* contract and `reveal` the rich one only where needed.
- **Refinement** (§4) — don't expose the representation (the 64 bytes) to clients at all; have them
  reason about an *abstract inode* and prove the representation refines it **once** at the boundary.

A proof assistant (§6 track D) is valuable as the *opacity/durability layer* on top of one of these —
never as a substitute for them.

## 3. Concept — Opacity (information hiding for specifications)

**Information hiding** (Parnas, 1972): a module exposes an *interface* and hides its *implementation*,
so clients depend only on what they need. **Opacity is the verification analogue:** a function has

- a **definition contract** — rich, verified *inside its owning unit* (here: the 18-field round-trip), and
- an **interface contract** — narrow, *what importers see* (here: `\length == 64`),

and the rich definition is **hidden by default**, *revealed* only in the proofs that need it. This is
simultaneously a **modularity** mechanism (clients don't couple to internals) and a **proof-cost**
mechanism (the solver isn't handed irrelevant hypotheses) — the two are the same act.

The state of the art (mapped to Dafny in §7):

- **Dafny** — `function {:opaque} f(...)` hides the body + rich post; `reveal f();` exposes it per
  proof; module **export sets** (`provides` vs `reveals`) narrow what importers get.
- **Coq/Rocq** — a lemma closed with `Qed` is **opaque**: clients see only its *statement* (type),
  never the proof term; `Module Type` interfaces give true separate compilation with narrowing.
- **F\*** — `.fsti` (interface) vs `.fst` (implementation); `--using_facts_from` *scopes which facts
  the SMT solver may use* (the direct proof-cost knob); `friend` for controlled access.
- **Separation logic** (VeriFast, VST/Iris) — predicates with `open`/`close` (fold/unfold) control
  when a rich definition enters the proof context.

**PyCSL's gap:** contracts are *all-or-nothing per function* and ride the import stub. Tracks **A**
(lemma extraction + selective `use` — opacity by hand) and **B** (opaque-on-export / `reveal` — opacity
as a feature) close exactly this gap.

## 4. Concept — Refinement (data refinement / the abstraction barrier)

**Data refinement** (Hoare, 1972): relate an **abstract value** to a **concrete representation** via
an **abstraction function** and a **coupling (representation) invariant**; prove operations correct
*at the abstract level*, discharging the representation↔abstract coherence **once**. Clients reason
about the abstract value and never unfold the representation — the *abstraction barrier*.

For the os codec the refinement is natural (it sits right on `_read_inode`/`_write_inode`):

```
_read_inode(n)      = _unpack_inode( disk[512+64n : +64] )
_write_inode(n, I)  = disk[512+64n : +64] := _pack_inode(I)
```

- **Abstract value:** an inode = an 18-field record (`ginode : int → inode_record`, ghost).
- **Concrete representation:** the 64-byte slice `disk[512+64n : +64]`.
- **Abstraction function:** `_unpack_inode` on the slice.
- **Coupling invariant:** `∀ n. ginode[n] == _unpack_inode(disk[512+64n : +64])`.
- **The one obligation:** `_write_inode(n, I)` re-establishes the invariant — this is where (and the
  **only** place where) the round-trip lemma is consumed.

Then the syscalls reason about `ginode[n]` (an abstract record) and **never unfold the 64-byte
codec** — so the 18 field-ensures *cannot* bloat them: the codec is below the barrier. Refinement
**dissolves** wall #3 rather than managing it.

Lineage: VDM (Jones), Z (Spivey), the refinement calculus (Back & von Wright; Morgan), Event-B
(Abrial), de Roever & Engelhardt's comparison; in automated tools, **Dafny**'s ghost-abstract-state
(`Valid()`) idiom and **Creusot**'s `view` (`@`) of a `Vec` as an immutable `Seq` (the same shape we
used for the seq-promotion model). Track **C** is this.

## 5. The role of HAPPY (region confinement) in refinement

The coupling invariant (§4) must be **preserved by every write**. The danger is *not* the inode being
written — it is the inodes that are **not**: `_write_inode(n, …)` must show it left inode `m ≠ n`'s
slice `disk[512+64m : +64]` untouched, or the coupling invariant for `m` breaks. Stated per-write,
that is a frame obligation over the whole 131072-byte disk at every call — the same blow-up risk in a
new place.

This is **exactly the region-confinement problem HAPPY solves** (see `happy.md` / `making-it-pure`).
A **HAPPY** is a whole-program integrity property that expands to a per-write `#@ check` at every
write site, sound with **no alias/call-graph analysis** (universal per-site coverage) and **0 backend
change**. Here it confines each `_write_inode(n, …)` to its slice:

> `_write_inode(n, …)` writes only `disk[512+64n : +64]` ⇒ every other inode's slice is preserved
> ⇒ the coupling invariant for `m ≠ n` holds **by confinement**, not by per-write whole-disk framing.

So the three concepts **compose**, and that composition is the principled end state:

```
HAPPY        frames the representation   (which disk bytes a write may touch)
Refinement   lifts to the abstract view  (syscalls see ginode, not bytes)
Opacity      hides the codec             (clients import the narrow contract)
```

HAPPY is the framing layer that makes refinement's coupling invariant affordable; refinement is what
removes the codec from the syscalls' view; opacity is what keeps the rich codec contract out of the
import. Track **C** uses HAPPY + refinement; tracks **A/B** provide the opacity; track **D** can supply
the durable, kernel-checked codec lemma underneath.

## 6. The four tracks (each gets its own detailed spec)

| Track | What it is | Concept | Cost | Owner | Detailed spec |
|---|---|---|---|---|---|
| **A** | **Lemma extraction + selective `use`** — keep `_pack_inode`'s exported contract at `\length == 64`; state the round-trip as a separate `lemma`/module that *only* faithfulness-needing clients `use`. 0657/0658 **are** that lemma; the missing piece is citing it inside a syscall proof without putting it on the stub. | Opacity (by hand, Why3-native) | **Lowest** — little/no new tool work | [STDLIB] + small [TOOL] | `A-*.md` (TBD) |
| **B** | **Opaque-on-export / `reveal`** — two contracts per function (narrow *interface* importers get; rich *definition* verified in the unit) + an explicit `#@ reveal`. Generalizes A into a feature; this is "contract narrowing on import." | Opacity (first-class) | Medium (a real tool feature) | [TOOL] | `B-*.md` (TBD) |
| **C** | **Data refinement / abstract inode view** — ghost `ginode` + coupling invariant; syscalls reason abstractly; round-trip consumed once at `_write_inode`; HAPPY confines each write (§5). | Refinement + HAPPY | Highest (refactor) | [STDLIB] + [TOOL] | `C-*.md` (TBD) |
| **D** | **Rocq/Lean bridge** — a kernel-checked, solver-independent proof of the codec round-trip, exposed to Why3 as an **opaque** lemma (statement only), kept out of the os import (via Why3's Coq/Isabelle realization). | Opacity + durability layer | Medium | [TOOL] + [FORMAL] | `D-*.md` (TBD) |

**How they relate.** **A** is a *special case* of **B** (manual vs first-class opacity). **A or C**
each deliver the immediate goal — os stays light while the round-trip is established — so one of them
is the near-term move (**A** is cheapest; **C** is the principled target and reuses HAPPY). **B** is
the force-multiplier if interface-narrowing recurs across modules (it will: every codec/serializer).
**D** is the *durability/opacity layer* over **A** or **C** — **never an alternative to them** (§2).
Recommended sequencing is detailed per-spec; the umbrella view: **A now → C as target → B if it
recurs → D for solver-independence.**

## 7. Comparison with Dafny (the closest analogue)

Dafny is the most directly comparable system: SMT-backed, auto-active, and it built precisely these
mechanisms — and treats opacity as a **proof-cost** tool, which is exactly PyCSL's 1700s symptom.

| PyCSL need / track | Dafny mechanism | Note |
|---|---|---|
| Narrow what a caller sees (A) | `function {:opaque} f` + `reveal f();` | hide the body+rich post by default; reveal per proof |
| Contract narrowing on import (B) | module **export sets**: `export E provides f reveals g` | importers pick an export set; `provides` = signature only, `reveals` = definition |
| Control solver unfolding (A/B) | `{:fuel f,0,0}` | tune how often a function definition is unrolled — Dafny's explicit anti-blow-up knob |
| Abstract inode view (C) | ghost-abstract-state idiom: concrete field + `ghost var Contents` + `predicate Valid()` (the coupling invariant), methods `requires/ensures Valid()` | the standard Dafny `Valid()` pattern *is* §4 |
| Codec round-trip as a reusable fact (A/D) | `lemma` (inert until invoked) | matches "extract the round-trip to a lemma, cite where needed" |
| Frame which state a write touches (§5 HAPPY) | dynamic frames: `reads`/`modifies` clauses + `{:opaque}` predicates | **closest analogue, but different**: Dafny frames via `modifies`; PyCSL frames via **HAPPY** (MetAcsl-style per-site `check`), which needs no alias/call-graph analysis and 0 backend change |

**Two differences worth stating.** (1) Dafny gets its framing from `modifies` clauses threaded through
every method; PyCSL's **HAPPY** is a *whole-program* confinement that expands to per-site checks — so
the §5 "writes only touch this inode's slice" property is one HAPPY, not a `modifies` clause on every
method. (2) Dafny designed opacity in from the start *as a performance feature*; PyCSL discovered the
need empirically (the import-stub bloat), which is why this umbrella exists before the feature (B) is
built. The lesson Dafny encodes — **opacity is a proof-cost mechanism, not only a modularity one** — is
the thesis of this document.

## 8. Soundness invariants across all four tracks

Whichever track lands, these hold (consistent with the project's soundness-ledger discipline):

1. **The round-trip is established, not assumed.** A/B/C consume the *proven* property (0657/0658 or
   its refinement obligation); they do not axiomatize it. D, *if it axiomatizes* the imported
   statement, adds the proof-assistant kernel + the Python→Lean translation to the **TCB** (a ledger
   entry); *if it replays*, it does not — the choice is recorded per the existing ledger practice.
2. **os return-code proofs are unaffected** — the point of all four tracks is that the codec's field
   values stop riding into syscall contexts that only prove return codes.
3. **Fail-safe.** A wrong *narrowing* (an interface contract that claims more than the definition
   proves) must **fail loud** — the definition unit's own proof catches it — never a wrong proof in a
   client. (The anti-`\trusted` invariant, applied to opacity.)
4. **Byte-identical corpus** for files that touch none of this; os holds at its current count or
   improves, never regresses.

## 9. Glossary

- **Opacity** — hiding a function's rich definition contract from clients by default; clients import a
  narrow *interface* contract and `reveal` the definition only where needed.
- **Interface vs definition contract** — the narrow contract importers see vs the rich contract
  verified inside the owning unit.
- **Refinement / data refinement** — relating an abstract value to a concrete representation via an
  abstraction function and a coupling invariant; reasoning abstractly, proving coherence once.
- **Abstraction function** — the map from representation to abstract value (here: `_unpack_inode`).
- **Coupling / representation invariant** — the predicate tying representation to abstract value
  (here: `∀n. ginode[n] == _unpack_inode(disk[512+64n:+64])`).
- **HAPPY** — a whole-program integrity (confinement) property expanding to a per-write `#@ check`,
  sound with no alias/call-graph analysis, 0 backend change (PyCSL's MetAcsl-HILARE analogue).
- **`reveal`** — opting a specific proof into a hidden definition.
- **fuel** — (Dafny) how many times the solver unfolds a function definition.
- **lemma function** — a separately-proven fact, inert until cited, that does not ride a function's
  call sites.

## 10. References

**Information hiding & opacity**
- D. L. Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules," *CACM* 15(12), 1972.
- K. R. M. Leino, "Dafny: An Automatic Program Verifier for Functional Correctness," *LPAR* 2010
  (opaque functions, `reveal`, fuel, ghost state; see also the Dafny Reference Manual for export sets).
- N. Swamy et al., "Dependent Types and Multi-Monadic Effects in F\*," *POPL* 2016 (interface files;
  `--using_facts_from` and `friend` in the F\* manual/tutorial).
- Y. Bertot, P. Castéran, *Interactive Theorem Proving and Program Development (Coq'Art)*, Springer
  2004 (`Qed` opacity vs `Defined`; `Opaque`/`Transparent`; `Module Type` interfaces).
- B. Jacobs, J. Smans, F. Piessens, "A Quick Tour of the VeriFast Program Verifier," *APLAS* 2010
  (predicate `open`/`close`).

**Refinement & data refinement**
- C. A. R. Hoare, "Proof of correctness of data representations," *Acta Informatica* 1(4), 1972
  (the foundational paper: abstraction function + representation invariant).
- C. B. Jones, *Systematic Software Development Using VDM*, 2nd ed., Prentice Hall, 1990.
- J. M. Spivey, *The Z Notation: A Reference Manual*, 2nd ed., Prentice Hall, 1992.
- R.-J. Back, J. von Wright, *Refinement Calculus: A Systematic Introduction*, Springer, 1998;
  C. Morgan, *Programming from Specifications*, 2nd ed., Prentice Hall, 1994.
- W.-P. de Roever, K. Engelhardt, *Data Refinement: Model-Oriented Proof Methods and their
  Comparison*, Cambridge, 1998.
- J.-R. Abrial, *Modeling in Event-B: System and Software Engineering*, Cambridge, 2010.
- X. Denis, J.-H. Jourdan, C. Marché, "Creusot: a Foundry for the Deductive Verification of Rust
  Programs," *ICFEM* 2022 (the `view`/`@` model); lineage: Y. Matsushita et al., "RustHorn,"
  *ESOP* 2020.

**Why3 (the PyCSL backend) & proof-assistant bridging**
- J.-C. Filliâtre, A. Paskevich, "Why3 — Where Programs Meet Provers," *ESOP* 2013 (and the Why3
  manual for module cloning/refinement and Coq/Isabelle/PVS *realizations*).

**SMT instantiation / large-array blow-up (wall #2 context)**
- L. de Moura, N. Bjørner, "Efficient E-matching for SMT Solvers," *CADE* 2007 (trigger-based
  quantifier instantiation — why irrelevant hypotheses cost).

**HAPPY / MetAcsl origin (§5)**
- V. Robles, N. Kosmatov, V. Prevosto, L. Rilling, P. Le Gall, "MetAcsl: Specification and
  Verification of High-Level Properties," *TACAS* 2019 (HILARE meta-properties, the assertion-expansion
  HAPPY mirrors).

**Project-internal**
- `try.md` — the inode round-trip retrospective (the three walls; §3.7–3.8 the module-granularity wall).
- `happy.md`, `making-it-pure*.md` — HAPPY confinement and the shared-World architecture.
- `07-1705-spec-rev4.md` — the seq-typed value model (Creusot-style `view`, the same refinement shape).
- `docs/pycsl-static-semantics-reference.md` — τ universe, RT/purity inference, module-import semantics.

> **In one line:** the inode round-trip is proven but cannot live in the os module because its rich
> contract rides the import stub into 8 syscall proofs that don't need it — a *specification-opacity /
> proof-context* problem, **not** a soundness, expressivity, or SMT one. The literature solves it with
> **opacity** (narrow the exported contract, reveal on demand — Dafny `{:opaque}`/export sets, Coq
> `Qed`, F\* interfaces) and **refinement** (reason over an abstract inode, prove the codec refines it
> once — with **HAPPY** confining each write so the coupling invariant stays affordable). A proof
> assistant (Rocq/Lean) is the *durability/opacity layer* over those, never a substitute. Tracks A
> (cheap, today), B (the feature), C (the principled target), and D (the durable layer) follow.
