# Handling aliasing in PyCSL

**Status:** Approved

## The problem in one paragraph

Python has **unrestricted mutable aliasing**. `def set(p, v): p.f = v` mutates whatever object the
caller passed, and two names can denote the same object. Why3/WhyML — PyCSL's verification backend
— deliberately does the opposite: it **forbids aliasing of mutable data** through a static
region/alias-control type system (Filliâtre & Paskevich, *Why3 — Where Programs Meet Provers*, ESOP
2013). That restriction is not an accident or a limitation to work around; it is *precisely* what
keeps Why3's verification conditions first-order and discharge­able by an SMT solver. So faithfully
modeling Python's mutate-through-alias semantics means importing a discipline Why3 intentionally
does not have. That is the real question behind "record-param mutation," and it is the one genuinely
research-grade item in PyCSL's backlog.

It is tempting to frame the choice as an open binary — *reason about arbitrary aliasing (separation
logic / dynamic frames) or impose an ownership discipline*. For PyCSL the decision is far more
constrained than that, for three reasons the generic framing misses.

## Three facts that constrain PyCSL's choice

**Fact 1 — PyCSL already ships dynamic frames.** The existing `assigns` clause (`#@ assigns
arr[0..n]`, `#@ assigns self._value`) *is* a dynamic frame in the sense of Kassios (*Dynamic
Frames*, FM 2006): a first-order specification of the set of locations a method may mutate. PyCSL is
not choosing between separation logic and dynamic frames in the abstract — it is **already on the
dynamic-frames branch**. The live question is narrower: *extend* that branch to cope with aliasing,
or *restrict* the input language so aliasing never arises. Switching to a separation-logic
foundation would mean discarding the `assigns` design and rebuilding on permission accounting — a
far larger move than the binary framing suggests.

**Fact 2 — PyCSL targets Why3; the proven Python recipe targets Viper.** The closest precedent is
**Nagini** (Eilers & Müller, *Nagini: A Static Verifier for Python*, CAV 2018), a modular verifier
for Python that handles arbitrary aliasing. It manages this because — like the underlying **Viper**
language — it uses **Implicit Dynamic Frames (IDF)**, a variant of separation logic: IDF establishes
a system of *permissions* for heap locations (roughly, separation logic's points-to predicates), a
method may read or write only locations it holds permission for, and a permission is created when a
field is first assigned. The recipe is proven and deployed — but it works because **Viper has IDF
built into the intermediate language**. Why3 does not. Transporting Nagini's approach to Why3 means
either re-implementing Viper's permission machinery *inside* WhyML, or switching backends. The
precedent here is loud: **Cameleer** — itself a Why3-based tool (Pereira & Ravara, CAV 2021) — found
this binding enough that it added a *separate Viper backend* to prove heap-dependent OCaml, rather
than push heap reasoning through Why3. That is a strong signal about Why3's grain.

**Fact 3 — heap reasoning is not PyCSL's value proposition.** The *CSL family's distinctive
contribution is **proof-assistant-sourced, cross-validated specifications** (`axiom_from`), not a
new heap logic. Building separation-logic-in-Why3 to handle arbitrary Python aliasing is exactly the
kind of generic, multi-year verifier engineering the family architecture is designed to *avoid*. Go
down the "faithfully model all aliasing" road and you spend two years rebuilding Viper inside Why3
while your actual contribution — the bridge — sits idle. That is the strategic trap.

## What each branch costs, read against Why3

| Approach | First-order / SMT-friendly? | Fit with Why3 | Verdict for PyCSL |
|---|---|---|---|
| **Separation logic** (Reynolds, LICS 2002) | No — `*` and points-to need encoding | The encodable fragment (Parkinson & Summers, ESOP 2011) *is* IDF → routes back to Viper | Foundation: **no** |
| **Implicit dynamic frames** (Smans–Jacobs–Piessens, ECOOP 2009) | Yes, via heap-dependent assertions | Native to Viper, **not** Why3 | Foundation: **no** (the Nagini path) |
| **Dynamic frames** (Kassios, FM 2006) | Yes, first-order by construction | This *is* what `assigns` already is | **Already here** |
| **Region logic** (Banerjee–Naumann–Rosenberg, ECOOP 2008) | Yes — sets + disjointness, never leaves FOL | The most Why3-compatible heap framework | **Escape hatch** |
| **Ownership** (Creusot/Rust; Jung et al., RustBelt) | Yes — by *forbidding* aliasing | Matches Why3's region system exactly | **Default** |
| **`modifies` clauses** (Dafny, Leino) | Yes | Dynamic-frames-flavored, closest to `assigns` | Reference point |

The one wall that no amount of region machinery removes: **reachability** — "what is reachable from
`p`" is a transitive closure, which is not first-order. Deep-heap framing over linked structures
with sharing hits this limit hard. That wall is where the novel move comes in.

## The choice — a four-part position

**Restrict aliasing by default; offer region-based dynamic frames as an explicit escape hatch; route
the genuinely hard (reachability) cases through proof-assistant-imported framing lemmas; never adopt
IDF/SL as the foundation.**

1. **Default memory model — an ownership boundary, working *with* Why3's grain.** Mutable objects
   are not aliased across method boundaries; passing a mutable object transfers (or stack-borrows)
   ownership. Code that mutates through an alias is **rejected at an ownership-check stage with a
   clear diagnostic**, not silently mis-verified. This preserves full SMT tractability, needs no new
   heap logic, and keeps `assigns` intact — `assigns` becomes the footprint of an *owned region*,
   which under the no-alias discipline is exactly what Why3's region system already understands.

2. **Escape hatch — region logic, not separation logic.** Where aliasing is genuinely needed, add a
   named-region surface built on Banerjee–Naumann–Rosenberg region logic — *not* IDF, *not* SL —
   because region logic stays first-order: regions are ghost `set loc` values, frame conditions are
   disjointness side-conditions (`R1 ∩ R2 = ∅`) the existing Why3→SMT path discharges. A directive
   surface like

   ```python
   #@ region R1 = self.reachable_fields()
   #@ assigns R1
   #@ requires \separated_region(R1, other_region)
   ```

   keeps the dynamic-frames flavor of `assigns` and never introduces the separating conjunction.

3. **The novel move — framing lemmas as `axiom_from` imports.** The reachability properties region
   logic cannot discharge automatically ("after this rotation the new spine is disjoint from the
   detached subtree", "this reversal permutes exactly the reachable cells") *can* be proved once, in
   Rocq or Lean, about a specific data structure — where transitive closure and induction over heap
   shape are natural — and imported via `#@ axiom_from rocq` / `#@ axiom_from lean`. The cross-check
   guarantees the two statements agree; the SMT solver then uses the imported lemma as a black-box
   first-order axiom. This is the proof-out philosophy applied to framing: the reasoning that does
   not fit SMT gets done in the proof assistant, and the bridge carries it across. As far as the
   literature shows, **this is novel** — nobody has used proof-assistant-imported framing lemmas as
   the mechanism for crossing the first-order reachability wall in an SMT-backed verifier. It is also
   the most natural demonstration that `axiom_from` earns its keep on a hard problem, not just on
   textbook GCD.

4. **Never adopt IDF/SL as the foundation.** The temptation to "do it properly" and build IDF into
   PyCSL to match Nagini means re-implementing Viper inside Why3 (huge, against the grain, the very
   thing Cameleer declined). If full IDF expressiveness is ever genuinely needed for some Python
   fragment, the right move is the **Cameleer move** — target Viper for *that fragment*, not rebuild
   Viper in Why3.

## The proximity with Creusot

Of all existing tools, **Creusot** (Denis, Jourdan & Marché, *Creusot: A Foundry for the Deductive
Verification of Rust Programs*, ICFEM 2022) is the family member closest to PyCSL in spirit, and it
is the strongest evidence that this position is right. Creusot:

- **Targets Why3** — the same backend, the same first-order/SMT discipline, the same region/alias
  type system at the root.
- **Solved aliasing by not having aliasing.** It exploits Rust's ownership discipline so that mutable
  borrows are never aliased, then models them with **prophecies** (a way to talk about the eventual
  value of a mutable borrow). It never builds separation logic; it stays on Why3 the whole time,
  *precisely because Rust's no-aliasing guarantee matches Why3's region system*.

PyCSL's default memory model is the **Creusot move transposed to Python**: where Creusot gets its
no-aliasing guarantee *for free* from the Rust type system, PyCSL must *establish* it with an
ownership/alias-check frontend pass (Python's type system does not provide it). But the destination
is identical — an owned, alias-free view of mutable state that Why3's region system reasons about
natively, with `assigns` as the owned footprint. Creusot is the existence proof that "restrict
aliasing, stay on Why3" is not a compromise but a coherent, productive design point; PyCSL reaches
the same conclusion for the same reasons, and adds the `axiom_from` framing-lemma move for the
reachability cases Creusot handles with prophecies.

The one structural difference worth stating plainly: Rust hands Creusot a *checked* ownership
discipline at the language level, so Creusot's frontend can trust it. Python hands PyCSL nothing, so
the ownership/alias check is **PyCSL's own obligation** — a frontend analysis that rejects programs
outside the discipline. That analysis is the real engineering cost of this position (see
`no-more-int-5.md` §A2b near-term plan, steps 1–2), and it is the price of targeting an unrestricted
language on an alias-free backend.

## A footnote that generalizes: JSON round-trip is the same shape

The `axiom_from`-framing-lemma idea (§3) is not a one-off. A verified JSON round-trip
`loads(dumps(x)) == x` is *also* a statement you prove once in Rocq/Lean and import — the
verified-serialization canon (**Narcissus**, Delaware et al., POPL/ICFP 2019; **EverParse/3D**,
Swamy et al.) tells you how to structure the proof; the bridge carries it across. So what looks like
two separate hard problems — heap framing and serialization round-trips — are the **same move**: a
proof-assistant lemma crossing a wall the SMT solver cannot climb on its own. That recurrence is the
sign the position is structural, not a patch.

## Why this is the right call for PyCSL specifically

- It works **with** Why3's region system instead of against it, preserving the SMT tractability that
  is Why3's whole reason for existing.
- It keeps the existing `assigns` design — the evolution is continuous, not a rewrite.
- It matches **Creusot**, the closest family member, which reached the same conclusion (restrict
  aliasing, stay on Why3) for the same reasons.
- It confines the unavoidable hard part (reachability) to the proof assistant, where it belongs, and
  routes it through the bridge already built.
- It does **not** turn PyCSL into a multi-year separation-logic engineering project competing with
  Nagini on Nagini's terms.

The honest cost — **idiomatic aliased-mutation Python is out of scope by default** — is the same cost
every successful Why3-targeting verifier has accepted. It is a documented, defensible *feature
boundary*, not a soundness gap.

## References

- Reynolds. *Separation Logic: A Logic for Shared Mutable Data Structures.* LICS 2002.
- Kassios. *Dynamic Frames: Support for Framing, Dependencies and Sharing Without Restrictions.* FM
  2006.
- Smans, Jacobs, Piessens. *Implicit Dynamic Frames.* ECOOP 2009; TOPLAS 34(1), 2012.
- Parkinson, Summers. *The Relationship Between Separation Logic and Implicit Dynamic Frames.* ESOP
  2011.
- Banerjee, Naumann, Rosenberg. *Regional Logic for Local Reasoning about Global Invariants.* ECOOP
  2008.
- Müller, Schwerhoff, Summers. *Viper: A Verification Infrastructure for Permission-Based Reasoning.*
  VMCAI 2016.
- Eilers, Müller. *Nagini: A Static Verifier for Python.* CAV 2018.
- Leino. *Dafny: An Automatic Program Verifier for Functional Correctness.* LPAR 2010.
- Denis, Jourdan, Marché. *Creusot: A Foundry for the Deductive Verification of Rust Programs.* ICFEM
  2022.
- Filliâtre, Paskevich. *Why3 — Where Programs Meet Provers.* ESOP 2013.
- Pereira, Ravara. *Cameleer.* CAV 2021.
- Delaware et al. *Narcissus: Correct-by-Construction Derivation of Decoders and Encoders from Binary
  Formats.* POPL/ICFP 2019.
- Jung et al. *RustBelt: Securing the Foundations of the Rust Programming Language.* POPL 2018.
