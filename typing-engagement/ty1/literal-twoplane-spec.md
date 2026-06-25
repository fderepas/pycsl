# `Literal` (PEP 586) — Two-Plane Spec

**Status:** Two-plane spec for the `Literal` construct. Authored by the typing-spec-agent
under the TY1 tier. This document carries the static claim, the runtime claim, the
divergence between them, and the Interpreted/Shimmed/Ignored classification — in four
sections that must NOT be merged. It cites the S1–S7 authorities per §3.1 of
`typing-global-impl.md` and proposes NO lowering (that is the core-agent's job); the
single mechanism named below — "ground requires" — is named only to confirm each static
clause is dischargeable by SOME mechanism, never to prescribe syntax. Each static
obligation clause is stated so it maps to one VC or one S5 conformance case; each runtime
claim is checked against S3's negative sentence (annotations are not enforced) resolved
by S4. `Literal` is fully sound — literal value sets are decidable — so NO GT gap is
tagged for it in this spec.

**Authorities cited in this spec:**
- **S1** — the typing specification (typing.readthedocs.io, Typing Council / PEP 729).
  S1 defines `Literal` semantics; literal value sets are a decidable, finite
  enumeration of concrete values.
- **S2** — PEP 586 (defining PEP for `Literal`). S1 supersedes S2 on any conflict.
- **S3** — the library reference (`docs.python.org/3/library/typing.html`); central
  sentence is NEGATIVE: the runtime does not enforce annotations.
- **S4** — CPython `Lib/typing.py` observable behaviour (the runtime lower bound).
- **S5** — the typing conformance test suite (static executable ground truth).
- **S7** — PyCSL front-end current behaviour (TY0 baseline; see VERDICTS.md).

---

## 1. STATIC PLANE

The static plane treats `Literal[v1, ..., vn]` as a finite enumeration of concrete
literal values: a value of type `Literal[v1, ..., vn]` is, at any program point, exactly
equal to one of `v1..vn`. The static meaning is a set of *judgments about programs* —
value-set membership, narrowing by equality, exhaustiveness, literal-kind restrictions,
and type equality — each stated below as an obligation clause precise enough to map to
one VC or one S5 conformance case. Nothing in this section claims anything happens at
runtime; runtime claims live in §2.

### 1.1 Value set (the load-bearing Literal clause)

- **L1 (value set, the load-bearing assignability rule).** A parameter annotated
  `x: Literal[v1, ..., vn]` means `x`'s value is exactly one of `v1, ..., vn`. The
  static obligation is `requires x == v1 or ... or x == vn` (ground requires). This is
  the load-bearing clause: it lowers, by the named "ground requires" mechanism (§1.6),
  to a single SMT-cheap disjunction of value equalities. — *cites S1, PEP 586 (S2).*
  Two S5 conformance cases pin it: (a) a value equal to some `v_i` flows in (accept);
  (b) a value equal to no `v_i` flows in (reject). The disjunction is finite and
  decidable, so the obligation is fully sound — there is no GT gap.

### 1.2 Narrowing by equality

- **L2 (narrowing by equality — the load-bearing Literal narrowing).** After
  `if x == v1:` where `x: Literal[v1, ..., vn]`, on the `True` branch `x` narrows to
  the singleton `Literal[v1]`; on the `False` branch `x` narrows to
  `Literal[v2, ..., vn]` (the value set minus `v1`, preserving order for L5). This is
  the static-plane narrowing for `Literal`: a value-equality test refines the
  enumeration. The narrowing is a proof-time path-condition judgment, NOT a runtime
  comparison the program performs (see D2). — *cites S1, PEP 586 (S2).* Two S5
  narrowing cases pin it (True-arm refines to `Literal[v1]`; False-arm drops `v1`).
- **L2a (chained equality narrowing).** Repeated `if x == v_i:` tests narrow the
  residual value set; after testing all but one value, the `False` branch narrows to
  the single remaining value. — *cites S1.* One S5 case per chained narrowing step.
- **L2b (`is None` for `Literal[None]`).** When `None` is one of the literal values,
  `if x is None:` narrows the `True` branch to `Literal[None]` (singleton) and the
  `False` branch to the residual enumeration, by analogy with L2 (identity test rather
  than equality test). — *cites S1, PEP 586 (S2).*

### 1.3 Exhaustiveness

- **L3 (match/if-chain exhaustiveness).** A `match` or `if/elif`-chain on a value of
  type `Literal[v1, ..., vn]` must cover every `v_i` (a case pattern accepting `v_i`
  for each `i`) OR end with a catch-all `else` / `case _:`. A non-exhaustive chain
  without a catch-all is a static error. — *cites S1, PEP 634 (S2 via S1), PEP 586 (S2).*
  One S5 case: an exhaustive chain over all `v_i` typechecks (accept); one S5 case: a
  non-exhaustive chain with no catch-all is rejected.

### 1.4 Literal kinds

- **L4 (supported literal kinds).** The supported literal kinds are: `int` literals,
  `str` literals, `bool` literals (which are `int` literals by S1), and the `None`
  literal (`Literal[None]` is the singleton type of `None`). These are the kinds PEP
  586 enumerates; the static plane treats each as a concrete ground value for the
  equality obligations in L1/L2. — *cites S1, PEP 586 (S2).*
- **L4a (bytes literals are NOT supported).** `bytes` literals (`b"..."`) are NOT
  permitted as `Literal` arguments. PEP 586 (S2) restricts `Literal` to `int`, `str`,
  `bool`, and `None` literals (and, separately, `Enum` members, which are a different
  concern handled by `Enum`'s own typing, not by this spec). A `Literal[b"x"]` form is
  a static error. — *cites PEP 586 (S2); S1 supersedes.*
- **L4b (Enum members — separate concern).** `Enum` members are a separate typing
  concern (handled by the `Enum` machinery, not by this spec); they are out of scope
  for the `Literal` value-set obligations here. — *cites PEP 586 (S2).*

### 1.5 Equality of Literal types

- **L5 (order-independent equality).** `Literal[1, 2]` and `Literal[2, 1]` denote the
  same static type (order-independent). The static-plane type-equality judgment treats
  two `Literal` types as equal iff their value sets are equal as sets. — *cites S1, PEP
  586 (S2).* One S5 case: `Literal[1, 2]` is assignable to `Literal[2, 1]` and vice
  versa (accept).
- **L5a (deduplication).** `Literal[1, 1]` and `Literal[1]` denote the same static
  type (duplicate literals are deduplicated). — *cites S1, PEP 586 (S2).* One S5 case:
  `Literal[1, 1]` is assignable to `Literal[1]` (accept).
- **L5b (single-argument degenerate).** `Literal[v]` (one argument) is the singleton
  type whose only value is `v`. — *cites S1, PEP 586 (S2).*
- **L5c (no nested Literal).** `Literal[Literal[1, 2]]` is a static error (PEP 586
  forbids nesting); `Literal` arguments must be literal values, not `Literal` types.
  — *cites PEP 586 (S2); S1 supersedes.* One S5 case: `Literal[Literal[1, 2]]` is
  rejected.

### 1.6 Expressibility check (dischargeability, NOT a lowering proposal)

Each clause above is stated so it can be discharged by SOME mechanism: the "ground
requires" mechanism (a `requires x == v1 or ... or x == vn` clause, per L1) makes the
value-set obligation a single SMT-cheap disjunction of concrete-value equalities, which
is decidable by construction (the value set is finite and enumerated). L2's narrowing
becomes a path-condition refinement of that disjunction (the `True` branch selects one
disjunct; the `False` branch drops it); L3's exhaustiveness becomes a coverage check
over the finite enumeration; L5's type-equality becomes set-equality on the enumerated
value set. The spec-agent confirms each clause is dischargeable by this mechanism; the
choice of mechanism was named in `typing-global-impl.md` §5 / the overview §4.2 (TY1
"Literal -> ground requires"), and `Literal` introduces no new mechanism. Because the
value set is finite and decidable, `Literal` is fully sound — no GT gap applies.

---

## 2. RUNTIME PLANE

The runtime plane says what `Literal` does when the program runs. S3's central sentence
is NEGATIVE: the Python runtime does NOT enforce function and variable type
annotations. So the runtime meaning of `Literal` is almost nothing — it is an
introspectable alias object, not a check.

### 2.1 `Literal[v1, ..., vn]` is a runtime alias object, not a check

- **LR1 (alias object identity).** `Literal[v1, ..., vn]` evaluates to an instance of
  `typing.Literal` (or, in modern CPython, an object whose `__origin__` is
  `typing.Literal`). It is a plain introspectable alias object; it is NOT a distinct
  runtime type. — *cites S3 (`typing.Literal`); resolved by S4 (`Lib/typing.py`'s
  `_LiteralGenericAlias`).*
- **LR2 (introspection).** `typing.get_origin(Literal[1, 2])` returns `typing.Literal`;
  `typing.get_args(Literal[1, 2])` returns `(1, 2)`. The literal values appear as
  themselves (not wrapped types). — *cites S3; resolved by S4.*
- **LR3 (no enforcement).** The runtime does NOT check that a value stored under a
  `Literal[v1, ..., vn]` annotation is one of `v1..vn`. Assigning a value of any type
  to a variable annotated `Literal[1, 2]` succeeds at runtime regardless of the value.
  — *cites S3 (central negative sentence).*

### 2.2 `isinstance` does NOT check Literal membership

- **LR4 (`isinstance` against `Literal`).** `isinstance(v, Literal[1, 2])` raises
  `TypeError` at runtime — `typing.Literal` aliases are not valid second arguments to
  `isinstance`. The runtime has no membership test for the literal value set. — *cites
  S3; resolved by S4.*

### 2.3 `x == v1` is the runtime test

- **LR5 (`x == v1` is the runtime test, NOT the static narrowing).** `x == v1` is the
  runtime equality comparison. It returns `True` iff `x` equals `v1` by Python's `==`
  semantics. This runtime test is what the static plane's narrowing (L2) keys on — but
  the runtime test and the static narrowing are DIFFERENT THINGS: the runtime test is a
  value-level comparison the program performs; the static narrowing is a proof-time
  path-condition judgment about a refined enumeration. The runtime test does NOT enforce
  the annotation (a value of any type can be compared with `== v1`), and the static
  narrowing does NOT require the runtime test to be executed. — *cites S3; resolved by
  S4.*
- **LR6 (no annotation enforcement, even with `== v1`).** Even when a program guards a
  `Literal[1, 2]`-typed variable with `if x == 1: ... else: <use x as Literal[2]>`, the
  runtime does NOT enforce that on the `else` branch `x` is `2`. The `==` test narrows
  the static type (L2); it does not narrow the runtime value's actual type. — *cites S3
  (central negative sentence).*

### 2.4 Identity / shim faithfulness

- **LR7 (no validation in the shim).** Any `src/pycsl_lib/typing` shim for `Literal`
  must agree with S4: it constructs the introspectable alias object and performs no
  validation of annotated values. A shim that CHECKED whether a value is one of `v1..vn`
  would be unfaithful in exactly the way an over-strong axiom is. — *cites S3, S4.*
- **LR8 (`Literal` is not a distinct runtime class).** A faithful shim does NOT
  introduce a distinct `Literal` runtime class; `Literal[v1, ..., vn]` must be the
  `typing.Literal` alias object, per LR1. Introducing a distinct `Literal` class would
  be an over-reification that diverges from S4. — *cites S3, S4.*

---

## 3. DIVERGENCE

The two planes disagree, and the disagreement is permanent: neither plane's claim may
stand in for the other. Stating them as a single contract is the canonical
coherent-and-wrong failure (typing edition). The `Literal` divergence is the
ground-requires-vs-alias-object specialization of the Union D1 / Optional OD1 split; the
same no-blend discipline applies, sharpened because the narrowing is by *value equality*
(L2), which is exactly where the temptation to blend is greatest.

- **LD1 (ground requires vs introspectable alias object).** The static plane (§1)
  treats `Literal[v1, ..., vn]` as the finite enumeration with value-set membership (L1),
  narrowing-by-equality (L2), exhaustiveness (L3), and literal-kind/type-equality (L4,
  L5) obligations — a judgment about programs. The runtime plane (§2) treats it as an
  introspectable `typing.Literal` alias object that enforces nothing (LR1–LR8). The
  static claim "this value is one of `v1..vn`" is NOT carried by the runtime alias
  object; the alias object does NOT check it. Specialization of Union D1.
- **LD2 (`x == v1` no-blend — the load-bearing Literal divergence).** The static plane
  (L2) treats `if x == v1:` as a narrowing guard that refines `Literal[v1, ..., vn]` to
  `Literal[v1]` (True branch) and the residual enumeration (False branch). The runtime
  plane (LR5) treats `x == v1` as a value-level equality comparison returning a `bool`.
  The two are DIFFERENT: the static narrowing is a proof-time path-condition judgment;
  the runtime test is a comparison the program performs. A lowering that let the
  runtime `x == v1` test's outcome SATISFY the L2 narrowing obligation would blend the
  planes: the static obligation must be discharged by a path-condition VC (the
  disjunct-selecting match on the ground-requires disjunction), independently of
  whether the program also runs the test. The runtime test narrows the VALUE
  (sometimes); the static narrowing narrows the TYPE (always, on the path).
  Specialization of Union D2 / Optional OD2 — sharpened because equality narrowing is
  THE load-bearing narrowing for `Literal`, so the temptation to blend is greatest
  here.
- **LD3 (no-blend invariant).** The static plane's obligations (§1) and the runtime
  plane's alias-object/introspection behaviour (§2) are carried as SEPARATE contracts,
  separately labelled. A `Literal` whose runtime shim passes a static conformance case
  is a finding (gap doc), not a success. The no-blend rule is defended by author
  separation: this spec-agent and the conformance-agent never read the core-agent's
  lowering. Specialization of Union D4.

---

## 4. CLASSIFICATION

- **Static plane: INTERPRETED (via ground requires).** `Literal[v1, ..., vn]` is
  consumed by the static plane and lowered — through the named "ground requires"
  mechanism, with no new mechanism — to obligations: value-set membership (L1),
  narrowing-by-equality (L2/L2a/L2b), exhaustiveness (L3), literal-kind restrictions
  (L4/L4a/L4b), and type equality (L5/L5a/L5b/L5c). Each clause maps to one VC or one
  S5 conformance case, discharged by the ground-requires disjunction of concrete-value
  equalities and its path-condition refinements. The construct is classified
  **Interpreted** in `--soundness-report`.
- **Runtime plane: SHIMMED.** The runtime meaning of `Literal[v1, ..., vn]` is the
  introspectable `typing.Literal` alias object with no enforcement (LR1–LR8). Any
  `src/pycsl_lib/typing` surface for `Literal` is a thin shim that constructs the alias
  object and performs no validation, introducing no distinct `Literal` class (LR8). The
  construct is classified **Shimmed** in `--soundness-report`.
- **Combined classification:** `Literal` is **Interpreted on the static plane, Shimmed
  on the runtime plane** — both classifications apply, separately, per the no-blend
  rule (§0/§3 of `typing-global-impl.md`). This is structurally identical to the Union
  / Optional classification, but the static mechanism is different (ground requires,
  not the sum-type variant) — which is the point: `Literal` is a finite enumeration of
  concrete values, discharged by SMT-cheap equality, not by per-arm constructors.

### GT gap codes tagged in this spec

No GT gap is tagged for `Literal`. `Literal` is fully sound: the literal value set is
finite, enumerated, and decidable (L1's disjunction is finite; L2's narrowing refines a
finite set; L3's exhaustiveness is a coverage check over a finite enumeration). There is
no `Any`-style gradual-consistency concern (L4 restricts literal kinds to int/str/bool/
None), no variance (monomorphic, no TypeVars), no `ParamSpec`/`TypeVarTuple`, no
polymorphic recursion, no forward-reference order beyond what TY0 owns, no
`# type: ignore`, and no runtime/static `Protocol`-style split.

The no-blend discipline (LD2 — the runtime `x == v1` test must not satisfy the L2 static
narrowing obligation) is restated here as a `Literal`-local specialization of the Union
D2 / Optional OD2 no-blend rule, NOT as a new GT code. It is the load-bearing
`Literal`-local restatement because equality narrowing is THE narrowing for `Literal`.
