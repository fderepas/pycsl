# `Optional` (PEP 484) — Two-Plane Spec

**Status:** Two-plane spec for the `Optional` construct. Authored by the typing-spec-agent
under the TY1 tier. This document is a THIN SPECIALIZATION of
`typing-engagement/ty1/union-twoplane-spec.md`: by S1's definition `Optional[X]` IS
`Union[X, None]` (PEP 484), and the coordinator's editorial decision #1 confirmed
`Optional` reuses the Union lowering seam (the Why3 variant with `Arm_None` as the
nullary constructor for the `None` arm). Shared clauses (syntax equivalence,
exhaustiveness, the `isinstance`/`TypeIs` narrowing families) are REFERENCED, not
duplicated; only the Optional-specific obligations — assignability of `None`, the
load-bearing `is None` narrowing, the runtime alias object — are stated here. Four
sections that must NOT be merged. Cites the S1–S7 authorities per §3.1 of
`typing-global-impl.md`. Proposes NO lowering (that is the core-agent's job); each
static obligation clause is stated so it maps to one VC or one S5 conformance case, and
each runtime claim is checked against S3's negative sentence resolved by S4.

**Authorities cited in this spec:**
- **S1** — the typing specification (typing.readthedocs.io, Typing Council / PEP 729).
  S1 defines `Optional[X]` as exactly `Union[X, None]`.
- **S2** — PEP 484 (introduces `Optional[X]` as the spelling of `Union[X, None]`).
  S1 supersedes S2 on any conflict.
- **S3** — the library reference (`docs.python.org/3/library/typing.html`); central
  sentence is NEGATIVE: the runtime does not enforce annotations.
- **S4** — CPython `Lib/typing.py` observable behaviour (the runtime lower bound).
- **S5** — the typing conformance test suite (static executable ground truth).
- **S7** — PyCSL front-end current behaviour (TY0 baseline; see VERDICTS.md).

**Inherits from:** `union-twoplane-spec.md` — clauses C1 (syntax equivalence),
C1a (idempotence/order), C1b (Unit/Optional equivalence, the definitional clause),
C1c (degenerate Union), C6 (`isinstance` narrowing), C7 (`TypeIs`/`TypeGuard`),
C8 (no narrowing without a guard), C9–C11 (exhaustiveness and post-match
assignability), C3 (reverse flow), C4 (`Any` arm, GT1), and the full runtime plane
R1–R8 carry over unchanged. This document restates only the Optional-specific
specializations of the assignability and `is None` narrowing clauses, and the
Optional-specific runtime alias claims.

---

## 1. STATIC PLANE

The static plane treats `Optional[X]` as, by definition, the sum type
`Union[X, None]`: a value of type `Optional[X]` is, at any program point, either a
value of `X` or the singleton `None`. Every static judgment about `Union[X, None]`
applies verbatim; this section states only the Optional-specific load-bearing
specializations. Nothing here claims anything happens at runtime; runtime claims
live in §2.

### 1.0 Definitional equivalence (PEP 484)

- **O1 (definitional).** `Optional[X]` denotes exactly the static type
  `Union[X, None]`. This is S1's definition (PEP 484, S2); it is not an
  approximation. Every static judgment that holds for `Union[X, None]` holds for
  `Optional[X]` and vice versa, with no remapping. — *cites S1, PEP 484 (S2).*
  This is the specialization of Union clause C1b.
- **O1a (no third arm).** `Optional[X]` has exactly two arms: `X` and `None`. There
  is no `Optional[X, Y]` spelling (it is a static error); `Optional` takes one
  argument. — *cites S1, PEP 484 (S2).*

### 1.1 Assignability

For a value `v` of static type `T` flowing into a target of static type
`Optional[X]` (i.e. `Union[X, None]`):

- **O2 (arm membership, the load-bearing Optional assignability rule).** `v` is
  assignable to `Optional[X]` iff `T` is `None` OR `T` is assignable to `X` under
  S1's assignability relation. This is the specialization of Union clause C2 to the
  two-arm case `{X, None}`. — *cites S1, PEP 484 (S2).* Two S5 conformance cases
  pin it: (a) a value of type `X` flows in (accept); (b) a value of type `None`
  flows in (accept).
- **O3 (None is always assignable).** A value of type `None` is assignable to
  `Optional[X]` for every `X`, unconditionally — including `Optional[Any]` (see
  O5) and `Optional[X]` where `X` is itself `None` (i.e. `Optional[None]` is
  `None`). This is the defining asymmetry of `Optional`: the `None` arm is always
  reachable. — *cites S1.* One S5 case: `None` flows into `Optional[X]` (accept).
- **O4 (reverse flow).** A value of type `Optional[X]` is assignable to a target
  of type `T` iff `X` is assignable to `T` AND `None` is assignable to `T`. The
  `None`-to-`T` obligation is the Optional-specific load: it fails whenever `T` is
  a non-`Optional` type that does not admit `None` (e.g. `int`, `str`), which is
  the static rejection of an un-narrowed `Optional[int]` flowing into an `int`.
  — *cites S1.* Specialization of Union clause C3.
- **O5 (`Any` argument — GT1 tagged).** If `X` is `Any` (`Optional[Any]`), the
  static plane does NOT import gradual consistency. `Optional[Any]` is treated as
  the two-arm union `{Any, None}` where `Any` is an opaque, operation-barren type
  (GT1); the `None` arm remains a fully-typed arm (O3 still holds), but the `Any`
  arm supports no operation without explicit narrowing. Every `Any` occurrence is
  reported in `--soundness-report`. `Optional[Any]` is NOT a universal sink.
  — *cites S1, GT1 (typing-global-overview.md §5).* Specialization of Union
  clause C4.

### 1.2 Narrowing

Narrowing is where `Optional` earns its keep: almost every use of `Optional[X]`
in real code is gated by an `if x is None:` test. The `is None` narrowing is the
load-bearing clause for `Optional`.

- **O6 (`is None` narrowing — the load-bearing Optional clause).** After
  `if x is None:` where `x: Optional[X]`, on the `True` branch `x` has type
  `None`; on the `False` branch `x` has type `X`. This is the specialization of
  Union clause C5 to the two-arm case `{X, None}`: the `True` branch selects the
  `None` arm (singleton), the `False` branch selects the `X` arm alone (there is
  no residual union). — *cites S1, PEP 484 (S2).* Two S5 narrowing cases pin it
  (True-arm refines to `None`; False-arm refines to `X`). This is the clause the
  Union lowering's `Arm_None` nullary constructor exists to discharge.
- **O7 (inherited narrowing families).** The `isinstance` narrowing (Union C6),
  the `TypeIs`/`TypeGuard` narrowing (Union C7), and the no-narrowing-without-a-
  guard rule (Union C8) apply to `Optional[X]` unchanged. For `Optional[X]`,
  `isinstance(x, C)` narrows by selecting whether `X` is assignable to `C`; the
  `None` arm is never selected by `isinstance` (since `None` is not an instance
  of any `C`). — *cites S1, PEP 484 (S2), PEP 742 (S2).*

### 1.3 Exhaustiveness

- **O8 (match exhaustiveness — inherited).** A `match` on a value of type
  `Optional[X]` must cover both arms: there must be a reachable case pattern that
  accepts a value of `X`, and a reachable case pattern that accepts `None` (e.g.
  `case None:` or `case _:`). Otherwise the match is non-exhaustive (a static
  error). — *cites S1, PEP 634 (S2 via S1).* Specialization of Union clause C9.
- **O9 (post-match assignability — inherited).** Union clause C10 applies
  unchanged: after an exhaustive match, the arm-bound variable is assignable to
  any target the arm type is assignable to, independently of the other arm.
  — *cites S1.*
- **O10 (unreachable arm — inherited).** Union clause C11 applies unchanged.
  — *cites S1.*

### 1.4 Expressibility check (dischargeability, NOT a lowering proposal)

Each clause above is stated so it can be discharged by the Union lowering the
core-agent has already chosen (the Why3 variant with `Arm_None` as a nullary
constructor and a per-`X` constructor for the `X` arm): O2/O3 become per-
constructor assignability obligations, with `Arm_None` carrying the always-`None`
case; O6's `is None` test becomes a match path condition selecting `Arm_None` on
the `True` branch and the `X` constructor on the `False` branch; O8's
exhaustiveness is a WhyML `match ... with` over both constructors. The spec-agent
confirms each clause is dischargeable by this mechanism; the choice of mechanism
was the core-agent's (for Union), and `Optional` introduces no new choice.

---

## 2. RUNTIME PLANE

The runtime plane says what `Optional` does when the program runs. S3's central
sentence is NEGATIVE: the Python runtime does NOT enforce function and variable
type annotations. So the runtime meaning of `Optional` is almost nothing — it is
an introspectable alias object, not a check. This section specializes the Union
runtime plane (clauses R1–R8) to `Optional`.

### 2.1 `Optional[X]` is a runtime alias object, not a check

- **OR1 (alias identity).** `Optional[X]` evaluates to the same object as
  `Union[X, None]`: an instance of `typing.Union` (or, in modern CPython, an
  object whose `__origin__` is `typing.Union`). `typing.Optional` is itself a
  plain alias for `typing.Union` with a single non-`None` arm; it is NOT a
  distinct runtime type. `Optional[X] is Union[X, None]` holds. — *cites S3
  (`typing.Optional`); resolved by S4 (`Lib/typing.py`'s `_UnionGenericAlias` and
  the `Optional = Union` aliasing).*
- **OR2 (introspection).** `typing.get_origin(Optional[X])` returns
  `typing.Union`; `typing.get_args(Optional[X])` returns `(X, NoneType)`. The
  `None` arm appears as `type(None)` (`NoneType`), not as the singleton `None`.
  — *cites S3; resolved by S4.* Specialization of Union R2.
- **OR3 (no enforcement).** The runtime does NOT check that a value stored under
  an `Optional[X]` annotation is `None` or of type `X`. Assigning a value of any
  type to a variable annotated `Optional[X]` succeeds at runtime regardless of the
  value's type. — *cites S3 (central negative sentence).* Specialization of Union
  R3.

### 2.2 `isinstance` does NOT check Optional membership

- **OR4 (`isinstance` against `Optional`).** `isinstance(v, Optional[X])`
  raises `TypeError` at runtime — `typing.Optional`/`typing.Union` aliases are
  not valid second arguments to `isinstance`. (Same asymmetry as Union R4: the
  PEP 604 spelling `X | None` DOES permit `isinstance` per Union R6, but the
  `Optional[X]` spelling does not.) — *cites S3; resolved by S4.*

### 2.3 `x is None` is the runtime test

- **OR5 (`is None` is the runtime test, NOT the static narrowing).** `x is None`
  is the runtime identity test against the singleton `None`. It returns `True`
  iff `x` IS the `None` singleton. This runtime test is what the static plane's
  `is None` narrowing (O6) keys on — but the runtime test and the static
  narrowing are DIFFERENT THINGS: the runtime test is a value-level comparison
  the program performs; the static narrowing is a proof-time judgment about a
  path condition. The runtime test does NOT enforce the annotation (a value of
  any type can be tested with `is None`), and the static narrowing does NOT
  require the runtime test to be executed. — *cites S3; resolved by S4.*
- **OR6 (no annotation enforcement, even with `is None`).** Even when a program
  guards an `Optional[X]`-typed variable with `if x is None: ... else: <use x as
  X>`, the runtime does NOT enforce that on the `else` branch `x` is of type
  `X`. The `is None` test narrows the static type (O6); it does not narrow the
  runtime value's actual type. — *cites S3 (central negative sentence).*

### 2.4 Identity / shim faithfulness

- **OR7 (no validation in the shim).** Any `src/pycsl_lib/typing` shim for
  `Optional` must agree with S4: it constructs the introspectable alias object
  (equivalent to `Union[X, None]`) and performs no validation of annotated
  values. A shim that CHECKED whether a value is `None` or of type `X` would be
  unfaithful in exactly the way an over-strong axiom is. — *cites S3, S4.*
  Specialization of Union R8.
- **OR8 (`Optional` is not a distinct object).** A faithful shim does NOT
  introduce a distinct `Optional` runtime class; `Optional[X]` must be the
  `Union[X, None]` object, per OR1. Introducing a distinct `Optional` class would
  be an over-reification that diverges from S4. — *cites S3, S4.*

---

## 3. DIVERGENCE

The two planes disagree, and the disagreement is permanent: neither plane's claim
may stand in for the other. Stating them as a single contract is the canonical
coherent-and-wrong failure (typing edition). The Optional divergence is the
two-arm specialization of the Union divergence; the same no-blend discipline
applies.

- **OD1 (sum type vs introspectable alias object).** The static plane (§1)
  treats `Optional[X]` as the two-arm sum type `Union[X, None]` with narrowing
  (O6), assignability (O2–O5), and exhaustiveness (O8–O10) obligations — a
  judgment about programs. The runtime plane (§2) treats it as an introspectable
  alias object (`typing.Optional` aliased to `typing.Union`) that enforces
  nothing (OR1–OR8). The static claim "this value is `X` or `None`" is NOT
  carried by the runtime alias object; the alias object does NOT check it.
  Specialization of Union D1.
- **OD2 (`is None` no-blend).** The static plane (O6) treats `if x is None:` as
  a narrowing guard that refines `Optional[X]` to `None` (True branch) and `X`
  (False branch). The runtime plane (OR5) treats `x is None` as a value-level
  identity test against the `None` singleton. The two are DIFFERENT: the static
  narrowing is a proof-time path-condition judgment; the runtime test is a
  comparison the program performs. A lowering that let the runtime `is None`
  test's outcome SATISFY the O6 narrowing obligation would blend the planes: the
  static obligation must be discharged by a path-condition VC (the `Arm_None`
  match arm), independently of whether the program also runs the test. The
  runtime test narrows the VALUE (sometimes); the static narrowing narrows the
  TYPE (always, on the path). Specialization of Union D2 — sharpened because
  `is None` is THE load-bearing narrowing for `Optional`, so the temptation to
  blend is greatest here.
- **OD3 (`Any` argument).** The static plane (O5) refuses `Any` as the `X` of
  `Optional[Any]` (GT1); the runtime plane (OR1–OR8) treats `Optional[Any]` as
  an introspectable alias object like any other. The runtime's acceptance of
  `Any` does NOT license the static plane to import gradual consistency; the
  `None` arm remains fully typed (O3) but the `Any` arm is opaque and
  operation-barren. Specialization of Union D3.
- **OD4 (no-blend invariant).** The static plane's obligations (§1) and the
  runtime plane's alias-object/introspection behaviour (§2) are carried as
  SEPARATE contracts, separately labelled. An `Optional` whose runtime shim
  passes a static conformance case is a finding (gap doc), not a success. The
  no-blend rule is defended by author separation: this spec-agent and the
  conformance-agent never read the core-agent's lowering. Specialization of Union
  D4.

---

## 4. CLASSIFICATION

- **Static plane: INTERPRETED (via Union seam).** `Optional[X]` is consumed by
  the static plane and lowered — through the Union lowering, with no new
  mechanism — to obligations: assignability (O2–O5), `is None` narrowing (O6),
  inherited narrowing families (O7), and exhaustiveness (O8–O10). Each clause
  maps to one VC or one S5 conformance case, discharged by the `Arm_None` /
  per-`X` constructor match. The construct is classified **Interpreted** in
  `--soundness-report`.
- **Runtime plane: SHIMMED.** The runtime meaning of `Optional[X]` is the
  introspectable alias object (`typing.Optional` aliased to `typing.Union`,
  equivalent to `Union[X, None]`) with no enforcement (OR1–OR8). Any
  `src/pycsl_lib/typing` surface for `Optional` is a thin shim that constructs
  the alias object and performs no validation, introducing no distinct
  `Optional` class (OR8). The construct is classified **Shimmed** in
  `--soundness-report`.
- **Combined classification:** `Optional` is **Interpreted on the static plane,
  Shimmed on the runtime plane** — both classifications apply, separately, per
  the no-blend rule (§0/§3 of `typing-global-impl.md`). This is identical to the
  Union classification, which is the point: `Optional` is `Union[X, None]` on
  every plane.

### GT gap codes tagged in this spec

- **GT1 — `Any` as the `X` of `Optional[Any]`.** Per O5 and OD3, the static
  plane refuses `Any` as the `X` argument (opaque, operation-barren, reported);
  the `None` arm remains fully typed. Tagged at O5 and OD3. Permanent, by design
  (typing-global-overview.md §5). Specialization of the Union GT1 tag.
- **GT7 — `runtime_checkable`-style runtime/static split.** `Optional` does NOT
  itself trigger GT7 (GT7 is owned by `Protocol` at TY2), but OD2 documents the
  no-blend discipline for `is None`: the runtime identity test must not be
  allowed to satisfy the O6 static narrowing obligation. This is an Optional-
  local restatement of the no-blend rule (sharpened from the Union-local
  restatement at Union D2 because `is None` is the load-bearing narrowing for
  `Optional`), not a new GT code.
- **GT8 — S5 conformance subset.** The S5 subset for `Optional` is the
  two-arm specialization of the Union subset: O2/O3 (assignability accept),
  O4 (reverse-flow reject), O6 (True/False narrowing), O8 (exhaustiveness
  reject). The conformance-agent builds this from the clause shapes above; it is
  the conformance-agent's standing artifact. Specialization of the Union GT8
  tag.

No other GT gap is tagged in this spec. GT2 (variance), GT3 (`ParamSpec`/
`TypeVarTuple`), GT4 (polymorphic recursion), GT5 (forward-reference resolution
order, owned by TY0), and GT6 (`# type: ignore`) are out of scope for `Optional`
at TY1 — `Optional` is monomorphic (`X` is a fixed type, not a TypeVar) and
introduces no forward-reference or ignore behaviour beyond what `Union` already
specifies.
