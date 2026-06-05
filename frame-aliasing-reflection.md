# The frame + aliasing problem for PyCSL — reflection and a way forward

## What the question actually is

Python has unrestricted mutable aliasing. `def set(p, v): p.f = v` mutates
whatever object the caller passed, and two names can denote the same
object. Why3/WhyML deliberately forbids aliasing of mutable data through
a static region/alias-control type system (Filliâtre & Paskevich, ESOP
2013); that restriction is *precisely* what keeps its VCs first-order
and SMT-friendly. Faithfully modeling Python's mutate-through-alias
semantics therefore means importing a discipline Why3 intentionally
does not have. That is the real research question, and the canon your
LLM listed is the right canon.

But the framing presented it as an open binary — "reason about
arbitrary aliasing (separation logic / dynamic frames) vs. impose an
ownership discipline." For PyCSL specifically the decision is more
constrained than that, for three reasons the generic framing misses.

## Three facts that constrain PyCSL's choice

**Fact 1 — PyCSL already ships dynamic frames.** The existing `assigns`
clause — `#@ assigns arr[0..n]`, `#@ assigns self._value` — *is* a
dynamic frame in the Kassios (FM 2006) sense: a specification of the set
of locations a method may mutate, written as a first-order expression
over the heap. You are not choosing between separation logic and dynamic
frames in the abstract; you have already built on the dynamic-frames
branch. The question is whether to *extend* that branch to cope with
aliasing, or to *restrict* the input language so aliasing never arises.
Switching to a separation-logic foundation would mean discarding the
`assigns` design and rebuilding on permission accounting — a much larger
move than the framing implied.

**Fact 2 — PyCSL targets Why3, and the proven recipe targets Viper.**
The closest precedent to your exact problem is Nagini (Eilers & Müller,
CAV 2018): a modular verifier for Python that handles arbitrary aliasing.
But Nagini achieves this because like the underlying Viper language, Nagini uses Implicit Dynamic Frames (IDF), a variation of separation logic, to achieve framing and allow local reasoning in the presence of concurrency, where IDF establishes a system of permissions for heap locations that roughly corresponds to separation logic's points-to predicates, methods may only read or write heap locations they currently hold a permission for, and can specify which permissions they require from and give back to their caller. The crucial detail: in Nagini, a permission is created when a field is assigned to for the first time. This recipe is proven and deployed — but it works because Viper has IDF *built into the intermediate language*. Why3 does not. Transporting Nagini's approach to Why3 means either re-implementing Viper's permission machinery inside WhyML (rebuilding a large part of Viper inside Why3) or switching backends. Cameleer — itself a Why3-based tool — found this so binding that it added a *separate Viper backend* specifically to prove heap-dependent OCaml, rather than push heap reasoning through Why3. That is a strong signal about Why3's grain.

**Fact 3 — heap reasoning is not PyCSL's value proposition.** The *CSL
family's distinctive contribution is proof-assistant-sourced,
cross-validated specifications (`axiom_from`), not a new heap logic.
Building separation-logic-in-Why3 to handle arbitrary Python aliasing
is exactly the kind of generic, multi-year verifier engineering the
family architecture is designed to *avoid*. If you go down the
"faithfully model all aliasing" road, you spend two years rebuilding
Viper inside Why3 and your actual contribution — the bridge — sits
idle. That is the strategic trap.

## What the literature says each branch costs, read against Why3

**Separation logic (Reynolds, LICS 2002).** The foundational answer to
framing. The frame rule (`{P} c {Q}` entails `{P * R} c {Q * R}` when
`c` doesn't touch `R`'s footprint) is exactly what you want. But raw SL
is not first-order; the separating conjunction and the points-to
predicate need encoding before an SMT solver sees them. Parkinson &
Summers (ESOP 2011) closed this gap precisely: a fragment of separation logic can be faithfully encoded in a first-order automatic verification tool. That theorem is the bridge that makes SL-style reasoning SMT-tractable — but the tool they encoded into was Chalice, an IDF-based verifier, not Why3. So "SL is SMT-encodable" is true and load-bearing, but the encoding *is* IDF, which routes you back to Fact 2.

**Dynamic frames (Kassios, FM 2006).** Framing via explicit sets of
locations, no SL syntactic restrictions, first-order by construction.
Closest to a Why3-native encoding and closest to what `assigns` already
is. The cost is annotation overhead: every method must specify its
footprint as a region expression, and you must thread these regions
through call sites and prove disjointness. This is the branch PyCSL is
already on.

**Implicit dynamic frames (Smans-Jacobs-Piessens, ECOOP 2009 / TOPLAS
2012).** The synthesis: permission accounting like SL, but expressed
through first-order assertions with heap-dependent expressions, so the
frame annotations are *implicit* in the access assertions rather than
written separately. This is what made Viper, and through Viper, Nagini,
Prusti, and Gobra. It is the state of the art for automated heap
reasoning with SMT backends. Its natural home is Viper, not Why3.

**Region logic (Banerjee-Naumann-Rosenberg).** First-order framing
built explicitly for SMT, using ghost state to track regions and
first-order disjointness side-conditions (`region1 ∩ region2 = ∅`) to
discharge frame conditions. This is the most Why3-compatible of the
heap-reasoning frameworks because it never leaves first-order logic —
no separating conjunction to encode, just sets and disjointness. The
known wall: reachability (the transitive closure "what is reachable
from p") is not first-order, so deep-heap framing (linked structures
with sharing) hits a hard limit that no amount of region machinery
removes.

**Ownership / RustBelt (Jung et al.); Creusot's prophecies (Denis et
al.).** The other branch entirely: don't reason about aliasing, forbid
it. Creusot exploits Rust's ownership discipline so that mutable
borrows are never aliased, then models them with prophecies — and it
stays on Why3 the whole time, precisely because Rust's no-aliasing
guarantee matches Why3's region system. This is the family member most
similar to PyCSL in spirit (Why3 backend, proof-assistant-adjacent),
and it solved the aliasing problem by *not having aliasing*.

**modifies-clause framing (Dafny, Leino).** Dafny's `modifies`/`reads`
clauses are dynamic-frames-flavored and the most directly transplantable
to PyCSL's `assigns`. Dafny accepts a real-but-bounded heap story: it
reasons about aliasing through `modifies` sets and frame conditions, but
its tractability rests on the programmer specifying footprints
diligently. It is the pragmatic midpoint and the closest existing tool
to "extended dynamic frames that mostly works."

## The recommendation

**Restrict aliasing by default; provide region-based dynamic frames as
an explicit escape hatch; never adopt separation logic as the
foundation.** Concretely, a four-part position:

### 1. Default memory model: ownership boundary, working with Why3's grain

Default to the discipline Why3 already enforces: mutable objects are not
aliased across method boundaries. This is the Creusot move. In Python
terms, it means PyCSL's default-verifiable subset treats each mutable
object as owned by one reference at a time; passing a mutable object to
a method transfers (or borrows, in a stack-disciplined way) that
ownership. Code that mutates through aliases is rejected at the
ownership-check stage with a clear diagnostic, not silently
mis-verified.

This preserves full SMT tractability, requires no new heap logic, and
keeps the existing `assigns` design intact — `assigns` becomes the
footprint of an owned region, which under the no-alias discipline is
exactly what Why3's region system already understands.

The cost is honest and must be documented: idiomatic
mutate-through-alias Python is out of scope by default. For the
self-hosting target (annotating pycsl's own source — mostly AST
transformations and largely functional data flow) this is comfortable.
For arbitrary third-party Python it is a real restriction, the same one
Creusot imposes on Rust and Dafny effectively imposes through its
discipline.

### 2. Escape hatch: region logic, not separation logic

For the cases where aliasing is genuinely needed, add an explicit
region/footprint annotation surface built on Banerjee-Naumann-Rosenberg
region logic — *not* IDF, *not* separation logic. The reason is Fact 2:
region logic stays first-order and stays in Why3's world. You encode
regions as ghost `set loc` values, frame conditions as disjointness
side-conditions, and let the existing Why3 → SMT path discharge them.

A directive surface like:

```python
#@ region R1 = self.reachable_fields()
#@ assigns R1
#@ requires \separated_region(R1, other_region)
```

keeps the dynamic-frames flavor of `assigns`, extends it to named
regions, and never introduces the separating conjunction.

Accept the reachability wall explicitly: deep-heap framing over linked
structures with sharing is not first-order and the escape hatch will not
handle it automatically. Which leads to the genuinely novel part.

### 3. The novel move: framing lemmas as `axiom_from` imports

This is where PyCSL's distinctive architecture turns the hardest part of
heap reasoning into an instance of the family pattern.

The reachability wall — "after this tree rotation, the new spine is
disjoint from the detached subtree," "this list reversal permutes
exactly the reachable cells" — is the class of property that first-order
region logic *cannot discharge automatically* because it requires
transitive-closure reasoning. But these properties *can* be proved, once,
in Rocq or Lean about your specific data structure, and imported as
axioms via `#@ axiom_from rocq` / `#@ axiom_from lean`.

So instead of building separation-logic machinery into PyCSL to make the
SMT solver derive these properties, you prove the framing lemma in a
proof assistant — where transitive closure and induction over heap shape
are natural — and cite it. The cross-check guarantees the Rocq and Lean
statements of the framing lemma agree. The SMT solver then uses the
imported lemma as a black-box first-order axiom.

This is exactly the proof-out philosophy applied to framing: the
reachability reasoning that doesn't fit SMT gets done in the proof
assistant, and the bridge carries it across. It is, as far as I can
tell from the literature, novel — nobody has used proof-assistant-imported
framing lemmas as the mechanism for crossing the first-order reachability
wall in an SMT-backed verifier. It is also the most natural possible
demonstration that the `axiom_from` mechanism earns its keep on hard
problems, not just on textbook GCD.

### 4. Never adopt IDF/SL as the foundation

The temptation will be to "do it properly" and build IDF into PyCSL so
it can match Nagini's expressiveness. Resist. That path means
re-implementing Viper inside Why3 (huge, fights the grain, documented as
binding enough that Cameleer added a Viper backend rather than attempt
it) and it produces a generic Python verifier whose distinctive
contribution — the bridge — is buried under heap-logic engineering. If
you ever genuinely need full IDF expressiveness for Python, the right
move is the Cameleer move: target Viper for that fragment, not rebuild
Viper in Why3. But for the *CSL family's actual goals, ownership +
region-logic escape hatch + imported framing lemmas covers the ground
that matters.

## Why this is the right call for PyCSL specifically

- It works *with* Why3's region system instead of against it, preserving
  the SMT tractability that is Why3's whole reason for existing.
- It keeps the existing `assigns` design, which is already dynamic
  frames; the evolution is continuous, not a rewrite.
- It matches Creusot — the family member most similar in spirit — which
  reached the same conclusion (restrict aliasing, stay on Why3) for the
  same reasons.
- It confines the unavoidable hard part (reachability) to the proof
  assistant, where it belongs, and routes it through the bridge you have
  already built.
- It does not turn PyCSL into a multi-year separation-logic engineering
  project that competes with Nagini on Nagini's terms.

The honest cost — idiomatic aliased-mutation Python is out of scope by
default — is the same cost every successful Why3-targeting verifier has
accepted. It is a feature boundary, documented and defensible, not a
soundness gap.

## On A4 (JSON round-trip) — not actually a separate problem

Your LLM correctly flagged Narcissus (Delaware et al., POPL 2019) and
EverParse/3D (Swamy et al.) as the verified-serialization canon, and
correctly noted this is "known recipe, not open trade-off." Worth
making the connection explicit: a round-trip theorem `decode ∘ encode =
id` is *exactly* the kind of statement you prove once in Rocq/Lean and
import via `axiom_from`. A4 is therefore not a separate research problem
at all — it is an application of the bridge to serialization. Prove the
round-trip property in both provers, cross-check, import as an axiom on
the Python `encode`/`decode` pair, and let Why3 use it. The Narcissus
techniques tell you *how to structure the proof* in the proof assistant;
the bridge handles getting it into PyCSL. This is a clean demonstration
that the family architecture absorbs "known-recipe" problems as
ordinary usage.

## A concrete near-term plan

1. **Specify the ownership discipline precisely** (1–2 weeks of design).
   Decide what "no aliasing across method boundaries" means in Python
   terms: parameter ownership transfer vs. stack-scoped borrowing,
   what `self` ownership means for methods, how immutable values (which
   can alias freely and safely) are distinguished. Creusot's borrow
   model and Dafny's `modifies` discipline are the two reference points.

2. **Build the ownership/alias checker as a frontend pass** (3–4 weeks).
   Before WhyML emission, run an analysis that rejects programs
   violating the discipline with clear diagnostics. This is the
   gatekeeper; it is what lets everything downstream stay in Why3's
   native region system. Existing alias-analysis literature (the
   Kotlin-on-Viper thesis approach of computing an alias graph per
   program point is one concrete recipe) applies.

3. **Keep `assigns` as-is; verify it now means "owned footprint."**
   Under the discipline, the existing `assigns` clauses gain a precise
   meaning with no syntax change.

4. **Prototype one imported framing lemma** (1–2 weeks). Pick a small
   heap-shape property (e.g., a list-reversal permutation lemma), prove
   it in Rocq and Lean, cross-check, import via `axiom_from`, and verify
   a Python list-reversal against it. This proves out the novel move (§3)
   on the smallest possible example.

5. **Defer the region-logic escape hatch** until a real test case demands
   it. Don't build the named-region machinery speculatively; build it
   when an actual program needs aliasing that ownership can't express.

6. **Write up the position.** The combination — ownership default + Why3
   region system + proof-assistant-imported framing lemmas for the
   reachability cases — is, as far as I can find, a new point in the
   design space, and the framing-lemma-import idea specifically is worth
   a paper.

## References

**Framing and aliasing canon:**

- Reynolds, J. C. *Separation Logic: A Logic for Shared Mutable Data
  Structures.* LICS 2002.
- O'Hearn, P. *Separation Logic.* CACM 62(2), 2019. (Modern overview.)
- Kassios, Y. *Dynamic Frames: Support for Framing, Dependencies and
  Sharing Without Restrictions.* FM 2006.
- Smans, J., Jacobs, B., Piessens, F. *Implicit Dynamic Frames:
  Combining Dynamic Frames and Separation Logic.* ECOOP 2009; extended
  in ACM TOPLAS 34(1), 2012.
- Parkinson, M., Summers, A. *The Relationship Between Separation Logic
  and Implicit Dynamic Frames.* ESOP 2011. (The first-order encodability
  result.)
- Banerjee, A., Naumann, D., Rosenberg, S. *Regional Logic for Local
  Reasoning about Global Invariants.* ECOOP 2008 (and the journal
  version). First-order, SMT-oriented framing.

**Tools and precedents:**

- Müller, P., Schwerhoff, M., Summers, A. J. *Viper: A Verification
  Infrastructure for Permission-Based Reasoning.* VMCAI 2016.
- Eilers, M., Müller, P. *Nagini: A Static Verifier for Python.* CAV
  2018. (The direct Python precedent — Python via Viper/IDF.)
- Leino, K. R. M. *Dafny: An Automatic Program Verifier for Functional
  Correctness.* LPAR 2010. (modifies/reads framing.)
- Denis, X., Jourdan, J.-H., Marché, C. *Creusot: A Foundry for the
  Deductive Verification of Rust Programs.* ICFEM 2022. (Ownership +
  Why3; the spiritually closest family member.)
- Filliâtre, J.-C., Paskevich, A. *Why3 — Where Programs Meet Provers.*
  ESOP 2013. (The region/alias-control type system at the root of the
  whole question.)
- Pereira, M., Ravara, A. *Cameleer.* CAV 2021, and the GOSPEL-to-Viper
  backend work. (The Why3-tool-that-added-a-Viper-backend precedent.)

**Verified serialization (for A4):**

- Delaware, B., et al. *Narcissus: Correct-by-Construction Derivation of
  Decoders and Encoders from Binary Formats.* POPL 2019 (ICFP 2019).
- Swamy, N., et al. *EverParse / 3D.* (Verified parser generation.)

**Ownership foundations (if the discipline route is pushed harder):**

- Jung, R., et al. *RustBelt: Securing the Foundations of the Rust
  Programming Language.* POPL 2018.
