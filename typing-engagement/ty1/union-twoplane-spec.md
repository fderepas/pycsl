# `Union` (PEP 484 / PEP 604) — Two-Plane Spec

**Status:** Two-plane spec for the `Union` construct. Authored by the typing-spec-agent
under the TY1 tier. This document carries the static claim, the runtime claim, the
divergence between them, and the Interpreted/Shimmed/Ignored classification — in four
sections that must NOT be merged. It cites the S1–S7 authorities per §3.1 of
`typing-global-impl.md` and proposes NO lowering (that is the core-agent's job). Each
static obligation clause is stated so it maps to one VC or one S5 conformance case; each
runtime claim is checked against S3's negative sentence (annotations are not enforced)
resolved by S4.

**Authorities cited in this spec:**
- **S1** — the typing specification (typing.readthedocs.io, Typing Council / PEP 729).
- **S2** — PEP 484 (type hints, the `Union[X, Y]` spelling) and PEP 604 (the `X | Y`
  spelling). S1 supersedes S2 on any conflict.
- **S3** — the library reference (`docs.python.org/3/library/typing.html`); central
  sentence is NEGATIVE: the runtime does not enforce annotations.
- **S4** — CPython `Lib/typing.py` observable behaviour (the runtime lower bound).
- **S5** — the typing conformance test suite (static executable ground truth).
- **S7** — PyCSL front-end current behaviour (TY0 baseline; see VERDICTS.md).

---

## 1. STATIC PLANE

The static plane treats `Union[A, B, ...]` (and the PEP 604 equivalent `A | B | ...`)
as a sum type: a value of type `Union[A, B]` is, at any program point, a value of
exactly one of the arms. The static meaning is a set of *judgments about programs* —
assignability, narrowing, exhaustiveness — each stated below as an obligation clause
precise enough to map to one VC or one S5 conformance case. Nothing in this section
claims anything happens at runtime; runtime claims live in §2.

### 1.0 Syntax equivalence (PEP 604)

- **C1 (syntax equivalence).** `Union[A, B]` and `A | B` denote the same static type.
  PEP 604 (S2) introduces `X | Y` as a surface spelling of `Union[X, Y]`; S1 treats
  them as the same construct for all static judgments below. — *cites S1, PEP 604 (S2).*
- **C1a (idempotence / order).** `Union[A, A]` is the same type as `A`; `Union[A, B]`
  and `Union[B, A]` are the same type. — *cites S1.*
- **C1b (Unit / Optional).** `Union[X, None]` is the type spelled `Optional[X]`; the
  two are interchangeable in every static judgment. — *cites S1, PEP 484 (S2).*
- **C1c (degenerate).** `Union[X]` (one arm) is the type `X`. — *cites S1.*

### 1.1 Assignability

For a value `v` of static type `T` flowing into a target of static type
`Union[A_1, ..., A_n]`:

- **C2 (arm membership, the load-bearing assignability rule).** `v` is assignable to
  `Union[A_1, ..., A_n]` iff there exists some `i` such that `T` is assignable to
  `A_i` under S1's assignability relation. — *cites S1.* This is one conformance case
  per arm: an S5 case where `v: A_i` flows in must typecheck, and an S5 case where
  `v: U` with `U` assignable to no arm must be rejected.
- **C3 (reverse flow).** A value of type `Union[A_1, ..., A_n]` is assignable to a
  target of type `T` iff *every* `A_i` is assignable to `T`. — *cites S1.* One S5 case
  per arm where the arm is assignable to `T` (accept) and one where some arm is not
  (reject).
- **C4 (Any arm — GT1 tagged).** If any arm `A_i` is `Any`, the static plane does NOT
  import gradual consistency. PyCSL treats `Any` in a Union arm as an opaque,
  operation-barren type (GT1); the assignability obligation above is discharged only
  against the non-`Any` arms, and every `Any` occurrence is reported in
  `--soundness-report`. The presence of `Any` does NOT make the Union a universal
  sink. — *cites S1, GT1 (typing-global-overview.md §5).*

### 1.2 Narrowing

Narrowing is the static-plane effect by which a runtime test (`is None`, `isinstance`,
`TypeIs`/`TypeGuard`) refines the static type of a variable on a control-flow path.
For `Union`, narrowing selects a subset of arms.

- **C5 (`is None` narrowing).** After `if x is None:` where `x: Union[A, None]`, on
  the `True` branch `x` has type `None`; on the `False` branch `x` has type `A` (or,
  for `Union[A, B, None]`, type `Union[A, B]`). — *cites S1, PEP 484 (S2).* One S5
  narrowing case per direction (True-arm refines to `None`; False-arm drops `None`).
- **C6 (`isinstance` narrowing).** After `if isinstance(x, C):` where
  `x: Union[A_1, ..., A_n]`, on the `True` branch `x` has the type of the sub-union
  of arms assignable to `C`; on the `False` branch `x` has the type of the sub-union
  of arms NOT assignable to `C`. If no arm is assignable to `C`, the `True` branch is
  statically unreachable (a dead-branch VC). — *cites S1, PEP 484 (S2).*
- **C7 (TypeIs / TypeGuard, PEP 742).** A guard function `g(x) -> TypeIs[T]` applied
  to `x: Union[...]` narrows `x` to `T` on the `True` branch and to
  `Union[...] \ T` on the `False` branch. `TypeGuard[T]` narrows the `True` branch
  only (the `False` branch is unchanged). — *cites S1, PEP 742 (S2).*
- **C8 (no narrowing without a guard).** In the absence of an `is None` /
  `isinstance` / `TypeIs` / `TypeGuard` test, the static type of a `Union`-typed
  variable is NOT refined by any other predicate (e.g. truthiness, attribute access).
  — *cites S1.* An S5 case where a narrowing is claimed without a guard must be
  rejected.

### 1.3 Exhaustiveness

- **C9 (match exhaustiveness).** A `match` on a value of type `Union[A_1, ..., A_n]`
  must cover every arm: for each `A_i` there must be a reachable case pattern that
  accepts a value of `A_i`, or the match is non-exhaustive (a static error). — *cites
  S1, PEP 634 (S2 via S1).*
- **C10 (post-match assignability).** After an exhaustive match where arm `i` is
  bound to a variable `y` of type `A_i`, `y` is assignable to any target `T` for
  which `A_i` is assignable to `T` — independently of the other arms. — *cites S1.*
- **C11 (unreachable arm).** If a case pattern accepts values that no arm of the
  Union can produce, that case is statically unreachable (dead code); PyCSL reports
  it. — *cites S1.*

### 1.4 Expressibility check (dischargeability, NOT a lowering proposal)

Each clause above is stated so that it can be discharged by SOME mechanism the
core-agent may choose: a sum-type (Why3 `type t = A | B | ...`) with one constructor
per arm makes C2/C3 a per-constructor obligation; an `is None` test becomes a match
path condition (C5); an `isinstance(x, C)` test becomes a match arm guard (C6); an
exhaustive match is a WhyML `match ... with` over all constructors (C9). The
spec-agent confirms each clause is dischargeable by some such mechanism; the choice
of mechanism is the core-agent's, not this spec's.

---

## 2. RUNTIME PLANE

The runtime plane says what `Union` does when the program runs. S3's central sentence
is NEGATIVE: the Python runtime does NOT enforce function and variable type
annotations. So the runtime meaning of `Union` is almost nothing — it is an
introspectable object, not a check.

### 2.1 `Union[X, Y]` is a runtime object, not a check

- **R1 (object identity).** `Union[X, Y]` evaluates to an instance of `typing.Union`
  (or, in modern CPython, an object whose `__origin__` is `typing.Union`).
  `Union[X, Y]` is `Union[Y, X]` and `Union[X, X] is X` (CPython collapses). — *cites
  S3 (`typing.Union`); resolved by S4 (`Lib/typing.py`'s `_UnionGenericAlias`).*
- **R2 (introspection).** `typing.get_origin(Union[X, Y])` returns `typing.Union`;
  `typing.get_args(Union[X, Y])` returns `(X, Y)`. — *cites S3; resolved by S4.*
- **R3 (no enforcement).** The runtime does NOT check that a value stored under a
  `Union[X, Y]` annotation is of type `X` or `Y`. Assigning a value of any type to a
  variable annotated `Union[X, Y]` succeeds at runtime regardless of the value's
  type. — *cites S3 (central negative sentence).*

### 2.2 `isinstance` does NOT check Union membership

- **R4 (`isinstance` against `Union`).** `isinstance(v, Union[X, Y])` raises
  `TypeError` at runtime — `typing.Union` aliases are not valid second arguments to
  `isinstance`. (This is the asymmetry with `int | str` below.) — *cites S3; resolved
  by S4.*

### 2.3 PEP 604 `X | Y` creates a `types.UnionType` object

- **R5 (PEP 604 runtime object).** `X | Y` (PEP 604) evaluates to an instance of
  `types.UnionType`, NOT `typing.Union`. Its `__origin__` is `types.UnionType`;
  `typing.get_args(X | Y)` returns `(X, Y)`. — *cites S3, PEP 604 (S2); resolved by
  S4.*
- **R6 (`isinstance` against `X | Y`).** Unlike `Union[X, Y]`, `isinstance(v, X | Y)`
  IS permitted at runtime (PEP 604): it returns `True` iff `isinstance(v, X)` or
  `isinstance(v, Y)` would return `True`. This is a runtime check on the value's
  concrete type, NOT an enforcement of the annotation. — *cites S3, PEP 604 (S2);
  resolved by S4.*
- **R7 (no annotation enforcement).** Even with R6, the runtime does NOT enforce
  that a value stored under an `x: X | Y` annotation satisfies the annotation; the
  `X | Y` object is the annotation's value, and `isinstance(v, X | Y)` is an explicit
  runtime check the program performs, not something the annotation does. — *cites S3
  (central negative sentence).*

### 2.4 Identity / shim faithfulness

- **R8 (no validation in the shim).** Any `src/pycsl_lib/typing` shim for `Union`
  must agree with S4: it constructs the introspectable object and performs no
  validation of annotated values. A shim that CHECKED whether a value belongs to a
  Union arm would be unfaithful in exactly the way an over-strong axiom is. — *cites
  S3, S4.*

---

## 3. DIVERGENCE

The two planes disagree, and the disagreement is permanent: neither plane's claim may
stand in for the other. Stating them as a single contract is the canonical
coherent-and-wrong failure (typing edition).

- **D1 (sum type vs introspectable object).** The static plane (§1) treats
  `Union[int, str]` as a sum type with narrowing, assignability, and exhaustiveness
  obligations — a judgment about programs. The runtime plane (§2) treats it as an
  opaque introspectable object (`typing.Union` alias or `types.UnionType`) that
  enforces nothing. The static claim "this value is an `int` or a `str`" is NOT
  carried by the runtime object; the runtime object does NOT check it.
- **D2 (`isinstance` asymmetry).** The static plane (C6) treats `isinstance(x, C)`
  as a narrowing guard that refines a Union type on each branch. The runtime plane
  (R4, R6) has two different behaviours: `isinstance(v, Union[X, Y])` raises
  `TypeError`, while `isinstance(v, X | Y)` performs a concrete-type membership
  test. NEITHER runtime behaviour is the static narrowing — the static narrowing is a
  proof-time judgment about a path condition, not a runtime check. A lowering that
  let `isinstance(v, X | Y)`'s runtime membership test satisfy the C6 narrowing
  obligation would blend the planes: the static obligation must be discharged by a
  path-condition VC, independently of whether the program also runs the check.
- **D3 (`Any` arm).** The static plane (C4) refuses `Any` as a Union arm (GT1); the
  runtime plane (R1–R8) treats `Union[Any, int]` as an introspectable object like
  any other. The runtime's acceptance of `Any` does NOT license the static plane to
  import gradual consistency.
- **D4 (no-blend invariant).** The static plane's obligations (§1) and the runtime
  plane's identity/introspection behaviour (§2) are carried as SEPARATE contracts,
  separately labelled. A `Union` whose runtime shim passes a static conformance case
  is a finding (gap doc), not a success. The no-blend rule is defended by author
  separation: this spec-agent and the conformance-agent never read the core-agent's
  lowering.

---

## 4. CLASSIFICATION

- **Static plane: INTERPRETED.** `Union[X, Y]` / `X | Y` is consumed by the static
  plane and lowered to obligations: assignability (C2/C3), narrowing (C5–C8), and
  exhaustiveness (C9–C11). Each clause maps to one VC or one S5 conformance case.
  The construct is classified **Interpreted** in `--soundness-report`.
- **Runtime plane: SHIMMED.** The runtime meaning of `Union[X, Y]` / `X | Y` is the
  introspectable object (`typing.Union` alias or `types.UnionType`) with no
  enforcement (R1–R8). Any `src/pycsl_lib/typing` surface for `Union` is a thin shim
  that constructs the object and performs no validation. The construct is classified
  **Shimmed** in `--soundness-report`.
- **Combined classification:** `Union` is **Interpreted on the static plane,
  Shimmed on the runtime plane** — both classifications apply, separately, per the
  no-blend rule (§3 of `typing-global-overview.md`).

### GT gap codes tagged in this spec

- **GT1 — `Any` in a Union arm.** Per C4 and D3, the static plane refuses `Any` as a
  Union arm (opaque, operation-barren, reported). Tagged at C4 and D3. Permanent, by
  design (typing-global-overview.md §5).
- **GT7 — `runtime_checkable`-style runtime/static split.** The Union construct does
  NOT itself trigger GT7 (GT7 is owned by `Protocol` at TY2), but D2 documents an
  analogous no-blend discipline for `isinstance` against `Union`/`X | Y`: the runtime
  check must not be allowed to satisfy the static narrowing obligation. This is a
  Union-local restatement of the no-blend rule, not a new GT code.
- **GT8 — S5 conformance subset.** The S5 subset for `Union` is not yet declared; it
  is the conformance-agent's standing artifact. Each clause C1–C11 above names the
  S5 case shape it commits to; the declared subset is built from those case shapes.

No other GT gap is tagged in this spec. GT2 (variance), GT3 (`ParamSpec`/
`TypeVarTuple`), GT4 (polymorphic recursion), GT5 (forward-reference resolution
order, owned by TY0), and GT6 (`# type: ignore`) are out of scope for `Union` at
TY1.
