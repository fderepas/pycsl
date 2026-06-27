# `TypeVar` / `Generic` (PEP 484 + PEP 695) — Two-Plane Spec

**Status:** Two-plane spec for the `TypeVar`/`Generic` construct (the TY3 generic layer).
Authored by the typing-spec-agent under the TY3 tier per `typing-global-impl.md` §2/§5.
This document carries the static claim, the runtime claim, the divergence between them,
and the Interpreted/Shimmed/Ignored classification — in four sections that must NOT be
merged. It cites the S1–S7 authorities per §3.1 and proposes NO lowering (that is the
core-agent's job). Each static obligation clause is stated so it maps to one VC or one S5
conformance case; each runtime claim is checked against S3's negative sentence (annotations
are not enforced) resolved by S4. The TY3 monomorphization no-blend trap — *an
un-instantiated generic must NOT claim a per-instance theorem it never emitted* — is the
load-bearing divergence (§3) and is the GT-trap the overview names for TY3.

**Authorities cited in this spec:**
- **S1** — the typing specification (typing.readthedocs.io, Typing Council / PEP 729).
  The "Generics", "Type variables", "Bounds", and PEP 695 "Type parameter syntax"
  sections are authoritative. Where S1 and PEP 484/695 (S2) conflict, S1 wins.
- **S2** — PEP 484 (Type Variables), PEP 695 (type-parameter syntax: `def f[T]`,
  `class C[T]`, `type X = ...`), PEP 612 (`ParamSpec`), PEP 646 (`TypeVarTuple`),
  PEP 673 (`Self`). Rationale and fine print; yields to S1 on conflict.
- **S3** — the library reference (`typing.html#typing.TypeVar`,
  `#typing.Generic`, `#typing.TypeVarTuple`, `#typing.ParamSpec`). The central sentence is
  NEGATIVE: the runtime does not enforce annotations. A `Generic` base / `TypeVar("T")`
  call constructs an introspectable *object*; it does NOT specialize code, does NOT check
  type arguments, and does NOT guarantee the bound at runtime.
- **S4** — CPython `Lib/typing.py` observable behaviour (the runtime lower bound the shim
  must be faithful to). `TypeVar("T", bound=int)` constructs a `TypeVar` instance whose
  `__bound__` attribute is `int`; `class C(Generic[T])` constructs a `_GenericAlias` /
  `GenericAlias` object recording the type parameters; `C[int]()` constructs an
  *ordinary instance* of `C` — no specialization occurs, no bound check runs, the type
  argument is recorded on `_parameters`/`__args__` for introspection only.
- **S5** — the typing conformance test suite (static executable ground truth). PyCSL
  declares the subset it conforms to (§1.5); the declared subset covers generic
  declaration, instantiation, bound, and the loud-fail cases (GT3/GT4).
- **S6** — the CPython 3.12 grammar / ASDL schema. The PEP 695 productions landed in
  `pure_ast.py` (commit 8335eede): `type_params` on `FunctionDef`/`ClassDef`, the
  `type_param` family (`TypeVar`/`ParamSpec`/`TypeVarTuple`), and the `TypeAlias`
  statement. Cited by the parser productions (S6, not this spec).
- **S7** — PyCSL front-end current behaviour (TY0 baseline). The front-end *parses*
  `class Stack[T]:` (PEP 695) and accepts `Stack[int]()` as a `Subscript`-`Call`, but the
  IR emitter drops `type_params` (it is not in `FunctionIR`/`TypeDecl`), so a generic is
  indistinguishable from a non-generic class in the IR today, and `Stack[int]()` is a
  plain constructor call with the type argument discarded. No collection, no emission, no
  per-instantiation theorem — this is the unspec'd de-facto behaviour TY0 pins and TY3
  replaces.

---

## 1. STATIC PLANE

The static plane treats a generic class/function `C[T]` as a **template**: a declaration
that is NOT itself a proof obligation. The proof obligations arise at each CONCRETE
instantiation `C[int]`, where the type variable `T` is replaced by the concrete type and
the entire class (fields, methods, contracts) is specialized to that concrete type. This is
**whole-module monomorphization**: collect every concrete instantiation in the closed
module, emit ONE name-mangled specialized copy per (generic, concrete-type) pair, prove
each copy as an ordinary monomorphic function. Nothing in this section claims anything
happens at runtime; runtime claims live in §2.

The static meaning is a set of *judgments about programs* — generic declaration,
instantiation collection, type substitution, bound satisfaction, the loud-fails (GT3/GT4)
— each stated below as an obligation clause precise enough to map to one VC or one S5
conformance case.

### 1.0 Syntax forms (PEP 484 + PEP 695)

- **G1 (generic class declaration, PEP 695).** `class C[T]: ...` (or `class C[T, U]:`)
  declares a generic class `C` parameterized by type variable `T`. `type_params` is
  non-empty on the `ClassDef`. The body declares fields and methods that may mention `T`
  in annotations and contracts. — *cites S1, PEP 695 (S2).*
- **G1a (generic function declaration, PEP 695).** `def f[T](x: T) -> T: ...` declares a
  generic function. `type_params` is non-empty on the `FunctionDef`. — *cites S1, PEP 695
  (S2).*
- **G1b (legacy `TypeVar("T")` spelling).** `T = TypeVar("T")` followed by
  `class C(Generic[T])` / `def f(x: T)` is the PEP 484 spelling. PEP 695 is preferred but
  the legacy form is interpreted identically (the `TypeVar` call + `Generic` base are
  recognized as declaring the type parameter). — *cites S1, PEP 484 (S2).*
- **G1c (bounded TypeVar).** `class C[T: B]` (or `T = TypeVar("T", bound=B)`) declares a
  **bound** `B`: a type argument `A` is admissible iff `A` is a subtype of `B`. The bound
  is an instantiation-time obligation (§1.3), NOT a runtime check. — *cites S1, PEP 484
  (S2).*

### 1.1 Instantiation collection (the load-bearing static rule)

- **G2 (COLLECT — closed-world instantiation).** A generic `C[T]` is discharged by
  monomorphization: the front-end scans the closed module for every **concrete
  instantiation** of `C` — i.e. every `C[<concrete-type>]` that flows into a value
  position (a constructor call `C[int]()`, an annotation `x: C[int]`, a type alias
  `type S = C[int]`). Each (generic, concrete-type) pair is one **instantiation site**.
  The set of concrete types is the set the generic is specialized to; an
  **un-instantiated** generic emits NO specialized copy (only its declaration is checked,
  §1.4). — *cites S1; the closed-module enabling assumption per the overview §4.1.*
  - *S5 mapping:* one case — a module with `Stack[int]()` and `Stack[str]()` collects
    exactly two instantiations; a module with `Stack[T]` and no instantiation collects
    zero and emits no specialized copy.

### 1.2 Specialized emission (name-mangled substitution)

- **G3 (EMIT — one name-mangled copy per instantiation).** For each instantiation site
  `(C, A)`, emit ONE specialized copy: the class is renamed `C_<A>` (e.g. `Stack_int`,
  `Stack_str`); the type variable `T` is substituted by `A` in (a) every field type, (b)
  every method signature (parameter and return), and (c) every contract clause
  (requires/ensures/assigns/class-invariant) that mentions `T`. The copy is then an
  ordinary monomorphic class proved as any non-generic class is. — *cites S1; the
  overview §4.1 "name-mangled specialized `let`/`val` per instantiation with substituted
  contracts".*
  - *S5 mapping:* one case — `Stack[int]` yields `Stack_int` whose `pop` returns `int`
    and whose `push` takes `int`; the int postcondition on `pop` is provable; a
    `Stack[str]` specialization returns `str` and is a SEPARATE proof (the str
    postcondition is not stateable on the int copy — this is the no-blend invariant, §3).
- **G3a (no per-instance theorem without emission).** An un-instantiated generic
  carries NO per-instance theorem. It is a *defect* (the no-blend trap) for the verifier
  to claim `Stack.pop` returns `int` when no `Stack_int` was emitted. The static plane
  refuses the claim: there is no obligation to prove and no theorem to assert. — *cites
  the overview §4.1 "an un-instantiated generic gets no program emission at all".*
  - *S5 mapping:* one reject case — a driver that asserts a per-instance property on a
    generic that was never instantiated with that concrete type MUST fail (no VC
    discharges because no specialized copy exists to carry the postcondition).

### 1.3 TypeVar bound — instantiation-time obligation

- **G4 (bound satisfaction at instantiation).** When `T` carries a bound `B`, each
  instantiation `C[A]` is admissible iff `A` is a subtype of `B`. This is an
  **instantiation-time obligation**: the front-end rejects `C[A]` where `A` is not a
  subtype of `B` (a static-plane check, NOT a runtime check — §2). — *cites S1, PEP 484
  (S2).*
  - *S5 mapping:* one pass case — `C[T: int]` instantiated with `int` is admissible; one
    reject case — `C[T: int]` instantiated with `str` is rejected with a located error.

### 1.4 Un-instantiated generic — declaration-only check

- **G5 (declaration-only check for un-instantiated generics).** A generic that is never
  instantiated in the module is NOT emitted as any specialized copy. Its declaration is
  checked for well-formedness (the bound is a valid type, the body parses, contracts are
  well-scoped) but NO method body is lowered to WhyML and NO VC is generated for its
  methods. The soundness report records it as **Ignored** (no instantiation → no
  obligation), tagged GT8 (the declared-subset discipline: no public conformance claim is
  made for a generic with no instantiation). — *cites the overview §4.1; GT8 (§5).*

### 1.5 Loud-fails (GT3, GT4)

- **G6 (GT4 — polymorphic recursion is a LOUD-FAIL).** Monomorphization does not
  terminate on polymorphic recursion (a generic function `f[T]` that calls `f[U]` with a
  fresh type variable `U` derived from `T`). The front-end REJECTS this with a dedicated
  error code rather than approximating. Detection: a generic method/function whose body
  calls the same generic with a type argument that is not one of the closed set of
  collected concrete instantiations. — *cites the overview §4.1, §5 GT4; S1.*
  - *S5 mapping:* one reject case — `def f[T](x): f[SomeOtherType]()` is rejected with a
    located error.
- **G7 (GT3 — `ParamSpec`/`TypeVarTuple` are schema-only).** The node layer carries
  `ParamSpec`/`TypeVarTuple` (S6/`_NODE_SPEC`); the static plane does NOT interpret them
  (no collection, no emission). A generic using `ParamSpec`/`TypeVarTuple` is REJECTED
  with a dedicated error code (schema-only, loud-fail). — *cites GT3 (§5).*
  - *S5 mapping:* one reject case — `def f[**P]():` is rejected with a located error.

### 1.6 Variance — deferred (GT2)

- **G8 (GT2 — variance is DEFERRED).** Co/contravariance of generic parameters (declared
  via `TypeVar("T", covariant=True)` or PEP 695-inferred) is NOT interpreted in TY3's
  first delivery. Instantiations are checked **invariantly** — `C[A]` requires `A` to be
  exactly the collected type, not a subtype. This is *stricter than S1* (which admits
  covariant/contravariant subtyping) and is legitimate divergence-by-strictness (§3). —
  *cites GT2 (§5).*

### 1.7 Declared S5 conformance subset

PyCSL declares the following S5 subset for the generic layer (the static gate, §Gate C):
- one generic declaration (PEP 695 `class C[T]`), parsed and IR-tracked with
  `type_params`;
- two concrete instantiations (`C[int]`, `C[str]`) yielding two name-mangled specialized
  copies, each with its substituted contract provable;
- one bound case (`C[T: int]` instantiated with `int` — admissible) and one reject case
  (instantiated with `str` — rejected);
- one un-instantiated generic (declaration-only, no specialized copy emitted);
- one polymorphic-recursion reject (GT4);
- one `ParamSpec`/`TypeVarTuple` reject (GT3).
A static claim with no corresponding S5 case is under-specified — gap doc.

---

## 2. RUNTIME PLANE

The runtime plane is *almost nothing*, by S3's central negative sentence: the runtime
does not enforce annotations. A `TypeVar`/`Generic` at runtime is an **introspectable
object**, not a specialization, not a check.

- **R1 (`TypeVar` constructs an object).** `T = TypeVar("T", bound=int)` constructs a
  `TypeVar` instance whose `__name__` is `"T"` and `__bound__` is `int`. No code is
  specialized; no check runs. — *cites S3, S4 (`Lib/typing.py:TypeVar`).*
- **R2 (`Generic` / `GenericAlias` is an introspectable object).** `class C(Generic[T])`
  / `class C[T]` makes `C` a class with a `__parameters__` tuple of its type variables.
  `C[int]` constructs a `GenericAlias`-like object recording `__args__ = (int,)` and
  `__origin__ = C`. `C[int]()` constructs an *ordinary instance* of `C` — the type
  argument is recorded on the instance's class, not used to specialize anything. — *cites
  S3, S4 (`Lib/typing.py:_GenericAlias`/`GenericAlias`).*
- **R3 (the bound is NOT checked at runtime).** `C[T: int]` instantiated with `str` at
  runtime (`C[str]()`) constructs an ordinary instance with NO bound check — the bound is
  a static-plane judgment (§1.3). A shim that CHECKED the bound at runtime would be
  unfaithful to S3's negative sentence. — *cites S3, S4.*
- **R4 (`cast`/`NewType` remain identities).** `cast(C[int], v)` returns `v` unchanged;
  `NewType("Name", C)` is a callable identity. No specialization, no check. (These are the
  TY1 shim; TY3 inherits them unchanged.) — *cites S3, S4; TY1 cast spec.*

The shim's contracts are therefore: `TypeVar(...)` returns an opaque introspectable
object (`#@ ensures \result == \result`, identity), `cast(C[int], v)` is `v` (identity),
and `C[int]()` is the ordinary constructor. No runtime-plane contract may assert a
per-instance theorem (§3).

---

## 3. DIVERGENCE (the no-blend trap, TY3 keystone)

The two planes disagree, and the disagreement is the load-bearing soundness argument for
the whole construct. The canonical TY3 trap, named explicitly by the overview §4.2:

> **An un-instantiated generic must NOT claim a per-instance theorem it never emitted.**

- **D1 (static per-instantiation theorem vs runtime generic-alias object).** The static
  plane produces a *per-instantiation theorem* — `Stack_int.pop` returns `int`, provable
  because the int specialization was emitted. The runtime plane produces a
  *generic-alias object* — `Stack[int]` is a `GenericAlias` recording `__args__=(int,)`,
  but `Stack[int]()` is an ordinary instance with NO specialized proof and NO per-instance
  postcondition. These are DIFFERENT things on DIFFERENT planes. Letting the runtime
  alias stand in for the static theorem — or encoding the static theorem into the runtime
  constructor — is the coherent-and-wrong failure, typing edition.
- **D2 (bound: static obligation vs runtime unchecked).** The bound is a static-plane
  instantiation obligation (§1.3, G4); at runtime it is unchecked (§2, R3). The two
  claims must NOT be merged: a shim that checked the bound would be unfaithful to S3.
- **D3 (variance: stricter than S1, deferred).** PyCSL checks instantiations invariantly
  (§1.6, G8); S1 admits variance. This is divergence-by-strictness — legitimate, recorded
  (GT2), not a bug. Neither plane's claim may stand in for the other.
- **D4 (polymorphic recursion: static loud-fail, runtime n/a).** Polymorphic recursion is
  a static-plane loud-fail (§1.5, G6/GT4); at runtime it is simply a recursive call with
  no check. The static rejection is the soundness guard; the runtime plane has nothing to
  say.
- **D5 (no-blend invariant, defended by independence).** The rule that the planes do not
  blend has NO external authority — it is defended by the independence of the spec-agent
  and conformance-agent from the core-agent (the overview's §4.2 argument). A lowering
  that quietly let the runtime generic-alias constructor satisfy the static
  per-instantiation theorem has no way to also fool a conformance subset authored from the
  static spec by someone who never saw the lowering. The Gate C (c) check is this guard.

---

## 4. CLASSIFICATION (Interpreted / Shimmed / Ignored)

Per `--soundness-report` extended taxonomy (overview §2.3):

- **Interpreted (static plane lowers to obligations):**
  - `class C[T]` / `def f[T]` declaration → well-formedness check + instantiation
    collection (G1/G1a/G1b, G2).
  - `C[<concrete-type>]` instantiation site → specialized emission with substituted
    contracts (G3), the load-bearing VC-bearing obligation.
  - `T: B` bound → instantiation-time obligation (G4).
  - Polymorphic recursion → loud-fail (G6/GT4).
- **Shimmed (runtime-plane meaning only):**
  - `TypeVar("T")` / `TypeVar("T", bound=B)` call → constructs an introspectable object
    (R1); the bound is recorded on `__bound__` but NOT checked (R3).
  - `Generic[T]` base / `C[int]` subscript → `GenericAlias` object (R2).
  - `cast(C[int], v)` / `NewType("N", C)` → identity (R4, inherited from TY1).
- **Ignored (outside the declared subset; reported with GT code):**
  - `ParamSpec` / `TypeVarTuple` (G7/GT3) — schema-only, loud-fail.
  - Variance (G8/GT2) — invariant checking, variance deferred.
  - `Any` as a type argument — refused (GT1): `Any` never instantiates a `TypeVar`
    (overview §4.1); an instantiation `C[Any]` is rejected, not approximated.
  - `# type: ignore` on a generic — never honoured (GT6).
  - An un-instantiated generic (G5) — declaration-only, no specialized copy; reported
    Ignored under GT8 (no conformance claim made).

### GT ledger (TY3 rows)

| GT | Disposition at TY3 | Acceptance line |
|---|---|---|
| GT1 `Any` | refused as a type argument | §4 Ignored; `C[Any]` rejected |
| GT2 variance | deferred — invariant checking | §1.6 G8; §3 D3 |
| GT3 `ParamSpec`/`TypeVarTuple` | schema-only loud-fail | §1.5 G7 |
| GT4 polymorphic recursion | loud-fail | §1.5 G6 |
| GT6 `# type: ignore` | never honoured (inherited) | §4 Ignored |
| GT8 declared S5 subset | the conformance gate | §1.7 |

---

## 5. NO LOWERING PROPOSED

This spec proposes no syntax, no IR fields, and no Module 6 emission. It states the
judgments; the core-agent (§2 of the impl guide) designs the COLLECT pass, the EMIT pass
(name-mangling + substitution), the bound check, and the GT4 loud-fail detector against
this spec, squeezed by sound expressibility (may be stricter than S1, never weaker) and
total additivity. A claim this spec cannot state without blending the planes (D1–D5) is a
finding, not something to merge.
