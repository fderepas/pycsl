# PyCSL Enhancement Proposal: Quantification over Sum Types, Sets, Classes, and Objects

**Status:** Draft / high-level design
**Scope:** Contract-expression language (`\forall` / `\exists`), static semantics, WhyML lowering
**Audience:** PyCSL maintainers, contract authors
**Non-goal:** implementation patches — this document specifies *what* must hold, not the diff.

---

## 1. Motivation

Today PyCSL's quantifiers bind a single **integer** index whose only sanctioned use is array
indexing: `\forall i; 0 <= i and i < n ==> arr[i] >= 0`. The transpiler emits `forall i : int`
unconditionally; the binder cannot range over any other type. Empirically, writing
`\forall j; P(j)` where `j` is meant to be a declared `#@ datatype` produces `forall j : int` and
then applies datatype functions to an `int`, yielding WhyML that the front end accepts but Why3
rejects as ill-typed.

This is a **front-end restriction, not a logic restriction.** Why3 is first-order logic with
polymorphic types: a quantifier may bind a variable of *any* type — algebraic/sum types,
records (the encoding of classes/objects), tuples, maps, and finite sets — and Why3 ships
recursive functions, recursive/inductive predicates, an `induction` transformation, and
existential-witness instantiation. The capability we want already exists one layer down; this
proposal lifts it into the PyCSL surface language in a sound, phased way.

## 2. Goals and non-goals

**Goals**

- Allow `\forall` / `\exists` to bind a variable of a **declared sum type** (`#@ datatype`),
  an **enum**, a **class** (record), a **set/finite collection**, or the existing scalar types
  (`int`, `bool`, `str`→string, `float`→real).
- Allow **bounded / membership-restricted** quantification: "for all elements of this set",
  "for all members of this collection".
- Allow contracts to state **whole-structure** and **whole-collection** properties that today
  can only be approximated with recursive predicate functions.
- Keep every accepted contract **type-sound at the WhyML level** (no false front-end greens).
- Integrate cleanly with the existing soundness story: anything requiring induction routes
  through the established `#@ proof` lemma-import mechanism.

**Non-goals**

- **Higher-order quantification.** Why3's logic is first-order: only *terms* may be quantified.
  Quantifying over predicates or functions (`\forall P; …`) is out of scope.
- **Unbounded "all allocated objects of class C" over a runtime heap.** The `hoare` memory model
  has no global object heap; object quantification is over record *values* or over an explicit
  ghost collection (see §6.4). True heap quantification is deferred to the `store`/`typed`
  models as future work.
- **Coinductive / infinite datatypes.**

## 3. Surface syntax

Quantifiers gain an **optional typed binder** and an **optional domain restriction**. The
integer-only forms remain valid and unchanged (full backward compatibility).

```
quant      ::= ("\forall" | "\exists" | "\exist") binders ";" pred
binders    ::= binder ("," binder)*
binder     ::= NAME                         # legacy: defaults to int
             | NAME ":" type                # typed binder
             | NAME "in" term               # membership-bounded binder
             | NAME ":" type "in" term      # typed + bounded
type       ::= "int" | "bool" | "str" | "float"
             | DATATYPE_NAME                # a name declared by #@ datatype
             | CLASS_NAME                   # a class defined in the module
             | "set" "[" type "]"           # finite set of element type
```

Domain restriction with `in` desugars to guarded quantification, exactly as the integer-range
idiom does today:

| Surface | Desugars to |
|---|---|
| `\forall x: T in S; P(x)` | `\forall x: T; member(x, S) ==> P(x)` |
| `\exists x: T in S; P(x)` | `\exists x: T; member(x, S) and P(x)` |
| `\forall i; 0 <= i and i < n ==> P` | unchanged (legacy integer range) |

Two optional control annotations support the proof layer (§7):

- `#@ trigger <pattern>` — placed on the same contract clause to override default e-matching
  trigger selection for the quantifier.
- `#@ by induction on <binder>` — placed on a clause whose obligation requires structural
  induction; routes to Why3's `induction` transformation or to an imported lemma (§8).

## 4. Worked examples (target state)

**Sum type — whole-structure property over JSON.** Replaces today's recursive-predicate
work-around with a direct binder where it reads naturally, while still permitting the predicate
form:

```python
#@ class invariant True
#@ ensures \forall n: int in \leaves(x); n >= 0   # "every integer leaf is non-negative"
```

**Enum — finite case coverage as a single clause:**

```python
#@ datatype Color = Red | Green | Blue
#@ ensures \forall c: Color; rank(c) >= 0 and rank(c) <= 2
```

**Class / object — invariant over a collection of accounts:**

```python
#@ class invariant self._balance >= 0
#@ requires \forall a: Account in self._accounts; a._balance >= 0
#@ ensures  \forall a: Account in self._accounts; a._balance >= \old_balance(a)
```

**Set — uniqueness / coverage:**

```python
#@ ensures \forall k: int in \keys(d); \exists v: int in \values(d); lookup(d, k) == v
```

## 5. Static semantics (Module 4 — Semantic Analyzer)

A typed/bounded quantifier is well-formed iff all of the following hold:

1. **Binder type is resolvable.** The annotated `type` is `int`/`bool`/`str`/`float`, or a name
   introduced by a `#@ datatype` in the same module, or a class defined in the module, or
   `set[T]` with `T` itself resolvable. Unknown names are a hard error (no silent `int` default).
2. **Legacy binders still default to `int`,** but only when the body's use of the binder is
   integer-typed; a binder used as a datatype value with no annotation is now an error, not a
   silent mis-lowering.
3. **Body is type-checked under the binder's type.** Every operation applied to the binder must
   typecheck against that type: datatype binders may appear in `match`-free contract terms only
   through pure projection/observer functions (`assigns \nothing` functions) and equality;
   class binders may use field access `b.field` and pure methods; set binders use membership and
   the element operations.
4. **Domain term is a collection of the binder's element type.** For `x: T in S`, `S` must have
   type `set[T]` (or a ghost collection whose element type is `T`).
5. **First-order check.** The binder ranges over a *data* type; binding a predicate or function
   symbol is rejected.
6. **Purity.** Any function/predicate called inside the quantifier body is pure
   (`assigns \nothing`), as already required for contract calls.

## 6. Lowering to WhyML (Module 6 — WhyML Transpiler)

The IR (Module 5 / `ir_schema`) gains a typed-binder node carrying `(name, why3_type,
optional_domain)`. Module 6 emits standard Why3:

### 6.1 Type mapping

| PyCSL binder type | Why3 binder type | Required `use` |
|---|---|---|
| `int` | `int` | `int.Int` |
| `bool` | `bool` | — |
| `str` | `string` | `string.String` |
| `float` | `real` | `real.Real` |
| `#@ datatype D` | `d` (the lowered algebraic type) | the emitted `type d` |
| class `C` | `c` (single-constructor record) | the emitted `type c` |
| `set[T]` | `fset t` | `set.Fset` |

### 6.2 Quantifier emission

```
\forall x: D; P            ->   forall x : d. P'
\exists x: D; P            ->   exists x : d. P'
\forall x: T in S; P       ->   forall x : t. mem x S' -> P'
\exists x: T in S; P       ->   exists x : t. mem x S' /\ P'
```

where `mem` is `Fset.mem` (finite sets) and `P'`, `S'` are the lowered body and domain.

### 6.3 Sets

Finite sets lower to Why3 `set.Fset`: `member` → `Fset.mem`, `\set_card` → `Fset.cardinal`,
union/inter/diff → the corresponding `Fset` operators. This supersedes the current
`map`-as-set ghost encoding for **quantification contexts**, where a real set theory gives the
solver membership lemmas. (The existing `ghost_set` map encoding remains available for mutable
ghost state.)

### 6.4 Classes and objects

A class is already lowered as a record/datatype value. Two quantification modes:

- **Over values:** `\forall o: C; inv_C(o) ==> P(o)` lowers to
  `forall o : c. inv_C o -> P' ` — a statement about every well-formed value of the record type.
  The class invariant must guard the quantifier (a raw `forall o : c` ranges over
  invariant-violating shapes too).
- **Over a ghost collection:** `\forall o: C in registry; P(o)` lowers via §6.2 membership.
  This is the recommended form for "all live objects": the program maintains an explicit ghost
  `set[C]` rather than relying on a heap the `hoare` model does not have.

## 7. Automation strategy: triggers

Quantification over rich types is only as good as the solver's ability to **instantiate** it.
PyCSL adopts surface-level trigger selection (as Dafny and Verus do) rather than leaving it to
the solver:

- **Default inference:** for each quantifier, Module 6 selects a trigger from the body's pure
  function calls / field accesses / membership terms that mention every bound variable, refusing
  patterns built only from interpreted symbols (`+`, `*`, `and`, nested quantifiers) to avoid
  matching loops.
- **Override:** `#@ trigger f(x), g(x)` emits `[f x, g x]` on the quantifier.
- **Diagnostics:** when no admissible trigger exists, Module 4 warns at annotation time (a
  quantifier with no good trigger is the dominant cause of "valid but never instantiated").

## 8. Soundness and the induction boundary

Adding the binder does not change the central fact established for recursive datatypes: a
universally quantified property over a recursive `#@ datatype` (e.g. agreement of two recursive
functions, or "a fold equals its spec for all trees") is **not first-order dischargeable** and
e-matching will not prove it. The specification therefore requires:

1. **No new trust.** A typed quantifier never becomes an axiom. It is a proof obligation like
   any other clause.
2. **Induction routing.** A clause carrying `#@ by induction on x` is discharged by Why3's
   `induction` transformation when applicable; otherwise it must be backed by an imported
   Rocq/Lean lemma through the existing `#@ proof` mechanism, with the same namespace-audit and
   reconciliation manifest that governs `#@ proof` today. A fabricated or unreconciled `#@ proof`
   citation continues to be rejected by the audit.
3. **Finite expansion fast-path.** For a **finite** sum type / enum, `\forall x: E; P(x)` is
   logically a finite conjunction; Module 6 may expand it to `P(C1) /\ P(C2) /\ … ` (one
   conjunct per nullary constructor) so the solver discharges it with no instantiation search and
   no induction. Constructors with payloads fall back to the general `forall x : e` form.

## 9. Interaction with existing features

- **`#@ datatype`:** the binder type vocabulary is exactly the set of declared datatypes plus
  the scalar types; mutually-recursive datatypes (corpus 0533/0534) are eligible binder types.
- **`#@ class invariant`:** becomes the canonical guard for value-mode object quantification
  (§6.4) and is auto-inserted as the antecedent.
- **`act` / `complete` / `disjoint` behaviors:** finite-enum `\forall` and an exhaustive `act`
  case-split are two views of the same finite analysis; the spec keeps both, with finite
  expansion (§8.3) as the bridge.
- **Recursive predicates:** remain fully supported and are the recommended encoding for
  whole-structure properties whose binder would otherwise need induction; the new syntax is
  additive, not a replacement.

## 10. Phasing

| Phase | Delivers | Risk |
|---|---|---|
| **P1 — Finite sum types / enums** | typed binder over nullary-only datatypes; finite-conjunction expansion (§8.3) | low; no instantiation, no induction |
| **P2 — Recursive datatypes** | `forall x : d` over recursive/mutually-recursive types; `#@ by induction on` + `#@ proof` routing | medium; induction obligations |
| **P3 — Sets & bounded quantification** | `set[T]` binder type, `x in S` desugaring, `Fset` lowering, trigger inference | medium; trigger brittleness |
| **P4 — Classes / objects** | value-mode (invariant-guarded) and ghost-collection-mode object quantification | high; heap/allocation modeling, deferred runtime-heap mode |

Each phase ships with corpus drivers following the existing numbering convention: a passing
demo and a deliberately-failing counterpart (gap/overlap, missing trigger, missing lemma) so the
validation stack exercises both outcomes.

## 11. Validation

- **Type-soundness gate:** every accepted typed quantifier must produce WhyML that Why3
  *typechecks* — closing the current false-green hole where `forall i : int` is emitted for a
  datatype binder. A CI check runs `why3 prove --type-only` (or equivalent) on generated `.mlw`
  for the quantification corpus, independent of SMT discharge.
- **Per-phase corpus:** P1 enum coverage; P2 tree/forest fold-vs-spec (induction lemma); P3 set
  membership + cardinality; P4 account-collection invariants. Each with a PASS and a FAIL twin.
- **Trigger regression:** a small suite asserting that default trigger inference selects
  loop-free patterns and that overrides take effect.

## 12. Open questions

1. **Runtime-heap object quantification.** Value-mode and ghost-collection-mode cover the
   common cases without a heap; should the `store`/`typed` models later expose a genuine
   `\forall o: C; \live(o) ==> …` with an allocation predicate analogous to ACSL `\valid`?
2. **Trigger policy for nested quantifiers.** Alternations (`\forall … \exists …`) are the
   classic source of instability; should P3 restrict to a single alternation depth initially?
3. **Set element decidable equality.** `Fset` requires decidable equality on the element type;
   datatypes with `str`/`real` payloads need a documented equality story before serving as set
   elements.
4. **Surface vs. desugared error locations.** Diagnostics should point at the `in S` clause the
   author wrote, not the desugared implication — requires source-span preservation through
   Module 3 / Module 5.
