# `TypedDict` (PEP 589) — Two-Plane Spec

**Status:** Two-plane spec for the `TypedDict` construct. Authored by the typing-spec-agent
under the TY2 tier. This document carries the static claim, the runtime claim, the
divergence between them, and the Interpreted/Shimmed/Ignored classification — in four
sections that must NOT be merged. It cites the S1–S7 authorities per §3.1 of
`typing-global-impl.md` and proposes NO lowering (that is the core-agent's job). Each
static obligation clause is stated so it maps to one VC or one S5 conformance case; each
runtime claim is checked against S3's negative sentence (annotations are not enforced)
resolved by S4.

**Authorities cited in this spec:**
- **S1** — the typing specification (typing.readthedocs.io, Typing Council / PEP 729).
  PEP 589 (S2) is the defining PEP; where S1 and PEP 589 conflict, S1 wins.
- **S2** — PEP 589 (TypedDict) and PEP 655 (Required/NotRequired, refined by S1). PEP 589
  defines the TypedDict semantics; PEP 655 introduces `Required`/`NotRequired` to mark
  individual keys as required/optional in a `total=False` TypedDict.
- **S3** — the library reference (`docs.python.org/3/library/typing.html#typing.TypedDict`);
  central sentence is NEGATIVE: the runtime does not enforce annotations.
- **S4** — CPython `Lib/typing.py` observable behaviour (the runtime lower bound): a
  TypedDict subclass is a plain `dict` at runtime (it IS a dict subclass).
- **S5** — the typing conformance test suite (static executable ground truth).
- **S7** — PyCSL front-end current behaviour (TY0 baseline): a `class X(TypedDict)`
  declaration is currently parsed as a *regular* `ast.ClassDef` whose `bases` contains
  `TypedDict`; `_collect_class_fields` returns the AnnAssign targets but emits an *empty*
  record (`type point = { }`) because TypedDict fields have annotation-only, no `__init__`
  assigns them. Field access `p["x"]` lowers to opaque `subscript_get p <hash>` (Why3
  rejects: `point` is not `int`). This is the unspec'd de-facto behaviour TY0 must pin.

---

## 1. STATIC PLANE

The static plane treats `class Point(TypedDict): x: int; y: int` as a *record type*: a
value of type `Point` is a value with two named fields `x` and `y`, each of a statically
fixed type. The static meaning is a set of *judgments about programs* — assignability,
field-access typing, construction typing, totality — each stated below as an obligation
clause precise enough to map to one VC or one S5 conformance case. Nothing in this section
claims anything happens at runtime; runtime claims live in §2.

### 1.0 Syntax forms (PEP 589 / PEP 655)

- **T1 (class form).** `class Point(TypedDict): x: int; y: int` declares a TypedDict type
  named `Point` with required keys `x: int` and `y: int`. — *cites S1, PEP 589 (S2).*
- **T1a (functional form).** `Point = TypedDict("Point", {"x": int, "y": int})` declares
  the same TypedDict. PyCSL commits to whichever form S5's subset uses; both spellings
  denote the same static type. — *cites S1, PEP 589 (S2).*
- **T1b (total=False).** `class Point(TypedDict, total=False): x: int; y: int` declares a
  TypedDict in which *all* keys are not-required unless explicitly marked `Required[T]`
  (PEP 655). PyCSL treats a `total=False` key as an *optional* field: its access yields
  `Optional[T]` (the field may be absent). — *cites S1, PEP 589 (S2), PEP 655 (S2).*
- **T1c (Required/NotRequired).** `Required[T]` marks a key required even in
  `total=False`; `NotRequired[T]` marks a key optional even in `total=True`. These spell
  per-key totality. — *cites S1, PEP 655 (S2).*

### 1.1 Assignability

For a value `v` of static type `T` flowing into a target of static type `Point` (a
TypedDict with required keys `k_i: T_i`):

- **T2 (record-shape assignability, the load-bearing rule).** `v` is assignable to `Point`
  iff (a) `T` is itself `Point`, or (b) `T` is a TypedDict with the *same key set* and,
  for each key `k_i`, the corresponding `T`-field's type is assignable to `T_i` under S1's
  assignability relation (structural subtyping, PEP 589 §"TypedDict Objects"). — *cites S1,
  PEP 589 (S2).* This is one conformance case per direction (a same-typed value flows in;
  a structurally-compatible TypedDict flows in; an incompatible TypedDict is rejected).
- **T3 (plain dict is NOT assignable).** A value of plain `dict` type is NOT assignable to
  `Point` (the dict's runtime shape is irrelevant; the static type carries the key-set
  obligation). Likewise a `Point` is NOT assignable to a plain `dict` target without an
  explicit cast. — *cites S1, PEP 589 (S2).* One S5 reject case each direction.
- **T4 (total vs partial).** A `total=False` TypedDict value is assignable to a
  `total=True` TypedDict of a *superset* of keys iff every required key of the target is
  present-and-typed-compatible in the source; this is structural subtyping on optional
  fields. PyCSL's record lowering models a `total=False` key as an `Optional[T]` field (see
  §1.4), so this reduces to per-field Optional-assignability — *cites S1, PEP 655 (S2).*

### 1.2 Field access

- **T5 (typed key access, the load-bearing typing rule).** For `p: Point` with
  `Point` declaring `x: int`, the expression `p["x"]` has static type `int`. The key must
  be a string *literal* known at type-check time (PEP 589 requires the key be a literal;
  a non-literal key is a static error). — *cites S1, PEP 589 (S2).* One S5 case per
  declared key (access yields the declared type); one reject case for an unknown key
  (`p["z"]` on a Point with no `z`); one reject case for a non-literal key.
- **T6 (required-key presence, total=True).** For `p: Point` (total=True) and a declared
  key `k: T`, `p["k"]` does NOT require a presence check — the static type guarantees the
  key is present, so the access yields `T` (not `Optional[T]`). — *cites S1, PEP 589 (S2).*
- **T7 (optional-key access, total=False / NotRequired).** For `p: Point` (total=False)
  and a declared not-required key `k: T`, `p["k"]` has type `Optional[T]` — a runtime
  `KeyError` is statically possible. The program MUST narrow with `if "k" in p:` before
  dereferencing without a `try`; otherwise the static plane emits a possible-KeyError VC.
  — *cites S1, PEP 655 (S2).*

### 1.3 Construction

- **T8 (typed construction).** The literal `{"x": 1, "y": 2}` (or `Point(x=1, y=2)` if the
  functional form is supported) is assignable to `Point` iff (a) every required key is
  present, (b) no key outside the declared set is present, (c) each value's type is
  assignable to the key's declared type. — *cites S1, PEP 589 (S2).* One S5 case per
  accept (well-typed literal) and reject (missing key, extra key, wrong-typed value).
- **T9 (missing/extra keys rejected, total=True).** A literal missing a required key or
  containing an undeclared key is a static error (type-check failure). For `total=False`,
  a missing optional key is accepted. — *cites S1, PEP 589 (S2).*

### 1.4 Expressibility check (dischargeability, NOT a lowering proposal)

Each clause above is stated so that it can be discharged by SOME mechanism the core-agent
may choose: a WhyML *record* `type point = { x: int; y: int }` makes T2 a record-type
equality, T5 a record-field read `p.x` (Why3 type-checks the field access against the
record definition), T8 a record literal `{ x = 1; y = 2 }` (Why3 type-checks each field
against the declared type and rejects missing/extra fields natively). A `total=False` key
is expressible as an `Optional[T]` field (reusing the TY1 Optional lowering) so T7 reduces
to Optional-narrowing. The spec-agent confirms each clause is dischargeable by some such
mechanism; the choice of mechanism is the core-agent's, not this spec's. **The core-agent's
hard rule (`typing-global-impl.md` §5, TY2): a TypedDict class synthesizes a WhyML record
`type td = { x: int; y: int }`, field access `p["x"]` becomes record-field access `p.x`,
construction `{"x": 1, "y": 2}` becomes a record literal. NO `\trusted`.**

---

## 2. RUNTIME PLANE

The runtime plane says what `TypedDict` does when the program runs. S3's central sentence
is NEGATIVE: the Python runtime does NOT enforce function and variable type annotations.
So the runtime meaning of `TypedDict` is almost nothing — a `TypedDict` subclass IS a
plain `dict` at runtime (S4: `_TypedDictMeta` extends `dict`'s metaclass; instances are
plain `dict` instances), and key/type enforcement happens *only* at type-check time.

### 2.1 `class X(TypedDict)` is a dict subclass at runtime

- **R1 (plain dict instance).** `class Point(TypedDict): x: int; y: int` produces, at
  runtime, a class `Point` whose instances are plain `dict` instances. `isinstance(p,
  dict)` is `True` for any `p: Point`. Constructing `{"x": 1, "y": 2}` produces a plain
  dict; assigning it to a `Point`-typed variable does NOT call any validator. — *cites S3
  (`typing.TypedDict`); resolved by S4 (`_TypedDictMeta` in `Lib/typing.py:3138+`).*
- **R2 (introspection).** `typing.get_type_hints(Point)` returns `{"x": int, "y": int}`;
  `Point.__total__` is `True` (or `False` for `total=False`); `Point.__required_keys__`
  and `Point.__optional_keys__` (PEP 655) report the per-key totality. These are
  introspection only — they do not enforce anything. — *cites S3; resolved by S4.*
- **R3 (no enforcement).** The runtime does NOT check that a value stored under a `Point`
  annotation has keys `x`, `y` of types `int`, `int`. Assigning `{"x": "string", "z": 1}`
  to a `Point`-typed variable succeeds at runtime regardless. A `KeyError` at `p["x"]` is
  a plain-dict `KeyError`, not an annotation-enforcement failure. — *cites S3 (central
  negative sentence); resolved by S4.*
- **R4 (no isinstance against TypedDict).** `isinstance(v, Point)` raises `TypeError` at
  runtime — `_TypedDictMeta.__instancecheck__` raises `TypeError('TypedDict does not
  support instance and class checks')` (S4: `Lib/typing.py:3268`). TypedDict types are
  not valid `isinstance` second arguments. — *cites S3; resolved by S4.*

### 2.2 Field access at runtime

- **R5 (subscript is dict subscript).** `p["x"]` at runtime is a plain dict subscript — it
  returns the dict's value for key `"x"` if present, else raises `KeyError`. There is no
  type-check; the value returned is whatever was stored. `p["x"] = v` is a plain dict
  store. — *cites S3; resolved by S4.*
- **R6 (no key/type check on subscript).** A subscript `p["z"]` for an undeclared key does
  NOT raise a TypedDict-specific error at runtime — it raises plain `KeyError` if `"z"` is
  absent, or returns the stored value if a program stored one (TypedDict does not prevent
  extra keys at runtime). — *cites S3; resolved by S4.*

### 2.3 Identity / shim faithfulness

- **R7 (no validation in the shim).** Any `src/pycsl_lib/typing` shim for `TypedDict` must
  agree with S4: it exposes the introspectable class object and performs NO validation of
  annotated values. A shim that CHECKED whether a value has the declared keys/types would
  be unfaithful in exactly the way an over-strong axiom is. — *cites S3, S4.*
- **R8 (plain-dict alias).** Because a TypedDict instance IS a plain dict, the runtime
  plane of a TypedDict-typed value is just the plain-dict plane (`dict.__getitem__`,
  `dict.__setitem__`, `dict.__contains__`). There is no separate TypedDict runtime
  behaviour beyond the class object's introspection methods. — *cites S3, S4.*

---

## 3. DIVERGENCE

The two planes disagree, and the disagreement is permanent: neither plane's claim may
stand in for the other. Stating them as a single contract is the canonical
coherent-and-wrong failure (typing edition).

- **D1 (record type vs plain dict).** The static plane (§1) treats `Point` as a record
  type with fixed-key, fixed-type fields — `p["x"]` is a record-field read typed `int`. The
  runtime plane (§2) treats `Point` as a plain dict — `p["x"]` is a dict subscript that
  returns whatever value was stored at key `"x"`, with no type guarantee. The static claim
  "this value's `x` field is an `int`" is NOT carried by the runtime dict; the runtime dict
  does NOT check it.
- **D2 (key-set enforcement).** The static plane (T8/T9) rejects literals with missing,
  extra, or wrong-typed keys at type-check time. The runtime plane (R1/R3/R6) accepts any
  dict literal as a TypedDict-typed value; extra keys are silently stored, missing keys
  surface only when the program dereferences them (as a plain `KeyError`). NEITHER runtime
  behaviour is the static typing rule.
- **D3 (isinstance).** The static plane uses structural subtyping (T2); `isinstance(v,
  Point)` is NOT the static conformance check (R4 raises `TypeError`). A lowering that let
  a runtime `isinstance`-or-presence check satisfy the static record-shape obligation
  would blend the planes.
- **D4 (no-blend invariant).** The static plane's obligations (§1) and the runtime plane's
  plain-dict behaviour (§2) are carried as SEPARATE contracts, separately labelled. A
  `TypedDict` whose runtime plain-dict alias passes a static field-access VC is a finding
  (gap doc), not a success. The no-blend rule is defended by author separation: this
  spec-agent and the conformance-agent never read the core-agent's lowering.

---

## 4. CLASSIFICATION

- **Static plane: INTERPRETED.** `class Point(TypedDict)` is consumed by the static plane
  and lowered to a record type declaration with one field per declared key; field access
  `p["x"]` lowers to a record-field read; construction `{"x": 1, "y": 2}` lowers to a
  record literal. Each clause T2–T9 maps to one VC or one S5 conformance case. The construct
  is classified **Interpreted** in `--soundness-report`.
- **Runtime plane: SHIMMED.** The runtime meaning of `TypedDict` is the plain-dict
  behaviour (a TypedDict instance IS a dict; subscripts are dict subscripts; no
  enforcement) plus the introspectable class object. Any `src/pycsl_lib/typing` surface for
  `TypedDict` is a thin shim that exposes the class object and performs no validation. The
  construct is classified **Shimmed** in `--soundness-report`.
- **Combined classification:** `TypedDict` is **Interpreted on the static plane, Shimmed
  on the runtime plane** — both classifications apply, separately, per the no-blend rule
  (§3 of `typing-global-overview.md`).

### GT gap codes tagged in this spec

- **GT7 — runtime/static split (analogous, NOT a new code).** D3 documents the
  `isinstance`-against-TypedDict asymmetry: the static T2 record-shape obligation must NOT
  be discharged by any runtime `isinstance`/presence check (R4 raises `TypeError`; even a
  `"x" in p` presence check is the dict-plane behaviour, not the static record-shape
  judgment). This is a TypedDict-local restatement of the no-blend rule, tagged in the
  report as a `no_blend_typeddict_isinstance` note, not a new GT code.
- **GT8 — S5 conformance subset.** The S5 subset for `TypedDict` is not yet declared; it
  is the conformance-agent's standing artifact. Each clause T2–T9 above names the S5 case
  shape it commits to; the declared subset is built from those case shapes.

No other GT gap is tagged in this spec. GT1 (`Any`), GT2 (variance), GT3
(`ParamSpec`/`TypeVarTuple`), GT4 (polymorphic recursion), GT5 (forward-reference
resolution order, owned by TY0), and GT6 (`# type: ignore`) are out of scope for
`TypedDict` at TY2.
