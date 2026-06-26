# `NamedTuple` (PEP 526) — Two-Plane Spec

**Status:** Two-plane spec for the `NamedTuple` construct. Authored by the typing-spec-agent
under the TY2 tier. This document carries the static claim, the runtime claim, the
divergence between them, and the Interpreted/Shimmed/Ignored classification — in four
sections that must NOT be merged. It cites the S1–S7 authorities per §3.1 of
`typing-global-impl.md` and proposes NO lowering (that is the core-agent's job). Each
static obligation clause is stated so it maps to one VC or one S5 conformance case; each
runtime claim is checked against S3's negative sentence (annotations are not enforced)
resolved by S4.

**Authorities cited in this spec:**
- **S1** — the typing specification (typing.readthedocs.io, Typing Council / PEP 729).
  PEP 526 (S2) is the defining PEP for the class-based `NamedTuple` syntax; where S1 and
  PEP 526 conflict, S1 wins.
- **S2** — PEP 526 (Syntax for Variable Annotations, §"Custom Class Bodies: NamedTuple")
  introduces the `class Point(NamedTuple): x: int; y: int` form. PEP 484 (S2) defines the
  functional form `Point = NamedTuple("Point", [("x", int), ("y", int)])`. `typing.NamedTuple`
  is the class-form marker; `collections.namedtuple` is the older functional factory.
- **S3** — the library reference (`docs.python.org/3/library/typing.html#typing.NamedTuple`);
  central sentence is NEGATIVE: the runtime does not enforce annotations.
- **S4** — CPython `Lib/typing.py` observable behaviour (the runtime lower bound): a
  `NamedTuple` subclass is a plain `tuple` at runtime (it IS a tuple subclass). Instances are
  constructed positionally and field names are accessible via `getattr`, but no type
  enforcement occurs.
- **S5** — the typing conformance test suite (static executable ground truth).
- **S7** — PyCSL front-end current behaviour (TY0 baseline): a `class X(NamedTuple)`
  declaration is currently parsed as a *regular* `ast.ClassDef` whose `bases` contains
  `NamedTuple`; the existing `_collect_class_fields` path returns an *empty* record because
  NamedTuple fields have annotation-only declarations with no `__init__` assigns them. The
  pre-existing `_synthesize_namedtuple_records` handles ONLY the functional
  `Name = namedtuple('Name', [...])` form (all-int fields), NOT the PEP 526 class form. This
  is the unspec'd de-facto behaviour TY0 must pin.

---

## 1. STATIC PLANE

The static plane treats `class Point(NamedTuple): x: int; y: int` as a *record type*: a
value of type `Point` is a value with two named fields `x` and `y`, each of a statically
fixed type, AND those fields are accessible positionally by declaration index (`p[0]` is
`x`, `p[1]` is `y`). The static meaning is a set of *judgments about programs* —
assignability, named-field access typing, positional-index access typing, construction
typing — each stated below as an obligation clause precise enough to map to one VC or one
S5 conformance case. Nothing in this section claims anything happens at runtime; runtime
claims live in §2.

### 1.0 Syntax forms (PEP 526 / PEP 484)

- **N1 (PEP 526 class form).** `class Point(NamedTuple): x: int; y: int` declares a
  NamedTuple type named `Point` with fields `x: int` and `y: int`, in declaration order.
  Field order is significant: it defines the positional index of each field. — *cites S1,
  PEP 526 (S2).*
- **N1a (functional form, typing.NamedTuple).** `Point = NamedTuple("Point", [("x", int),
  ("y", int)])` declares the same NamedTuple. PyCSL commits to whichever form S5's subset
  uses; both spellings denote the same static type. — *cites S1, PEP 484 (S2).*
- **N1b (default values).** `class Point(NamedTuple): x: int = 0; y: int = 0` declares
  fields with defaults (PEP 526). A field with a default makes trailing positional
  construction arguments optional. PyCSL's record lowering models a default as the field's
  `field_default` (the existing record convention); construction must still provide every
  field positionally in the S5 subset PyCSL declares. — *cites S1, PEP 526 (S2).*

### 1.1 Assignability

For a value `v` of static type `T` flowing into a target of static type `Point` (a
NamedTuple with fields `f_i: T_i` in order):

- **N2 (record-shape assignability, the load-bearing rule).** `v` is assignable to `Point`
  iff `T` is itself `Point` (nominal — a NamedTuple type is nominal, not structural, per
  PEP 526 / PEP 484). A different NamedTuple type is NOT assignable even with the same
  field names/types. — *cites S1, PEP 526 (S2).* One conformance case: a same-typed value
  flows in; one reject case: a structurally-identical-but-differently-named NamedTuple is
  rejected.
- **N3 (plain tuple is NOT assignable).** A value of plain `tuple` type is NOT assignable
  to `Point` (the tuple's runtime shape is irrelevant; the static type carries the
  named-field obligation). Likewise a `Point` is NOT assignable to a plain `tuple` target
  without an explicit cast. — *cites S1, PEP 484 (S2).* One S5 reject case each direction.

### 1.2 Named field access

- **N4 (typed named-field access, the load-bearing typing rule).** For `p: Point` with
  `Point` declaring `x: int`, the expression `p.x` (attribute access) has static type `int`.
  The attribute name must be a declared field (a non-declared attribute access is a static
  error). — *cites S1, PEP 526 (S2).* One S5 case per declared field (access yields the
  declared type); one reject case for an unknown attribute (`p.z` on a Point with no `z`).

### 1.3 Positional index access

- **N5 (typed positional access, the load-bearing typing rule).** For `p: Point` with
  `Point` declaring `x: int, y: int` (in that order), the expression `p[0]` has static type
  `int` (the type of field `x`), and `p[1]` has static type `int` (the type of field `y`).
  The index must be an integer *literal* known at type-check time (a non-literal index is a
  static error; an out-of-range literal index is a static error). The positional index maps
  to the field at that declaration index. — *cites S1, PEP 526 (S2).* One S5 case per
  declared field index (access yields the declared type); one reject case for an
  out-of-range index (`p[2]` on a 2-field Point); one reject case for a non-literal index.

### 1.4 Construction

- **N6 (typed positional construction).** The call `Point(1, 2)` (positional construction)
  is assignable to `Point` iff (a) the number of arguments equals the number of declared
  fields (minus fields with defaults, per N1b), (b) each argument's type is assignable to
  the corresponding field's declared type, in declaration order. — *cites S1, PEP 526 (S2).*
  One S5 case per accept (well-typed positional construction) and reject (wrong arity,
  wrong-typed argument).
- **N7 (wrong arity rejected).** A call `Point(1)` (too few) or `Point(1, 2, 3)` (too many)
  is a static error (type-check failure). — *cites S1, PEP 526 (S2).*

### 1.5 Expressibility check (dischargeability, NOT a lowering proposal)

Each clause above is stated so that it can be discharged by SOME mechanism the core-agent
may choose: a WhyML *record* `type point = { x: int; y: int }` makes N2 a record-type
equality, N4 a record-field read `p.x` (Why3 type-checks the field access against the
record definition), N6 a record literal `{ x = 1; y = 2 }` (Why3 type-checks each field
against the declared type and rejects wrong arity natively). N5 (positional access `p[0]`)
is expressible as a record-field read by *index*: the core-agent maps the literal index to
the field at that declaration position and emits the corresponding record-field read
(`p[0]` → `p.x`, `p[1]` → `p.y`). The spec-agent confirms each clause is dischargeable by
some such mechanism; the choice of mechanism is the core-agent's, not this spec's. **The
core-agent's hard rule (`typing-global-impl.md` §5, TY2): a NamedTuple class synthesizes a
WhyML record `type nt = { x: int; y: int }` (reusing the TypedDict record seam), named
field access `p.x` becomes record-field access, positional access `p[0]` becomes
record-field access by index, construction `Point(1, 2)` becomes a record literal. NO
`\trusted`.**

---

## 2. RUNTIME PLANE

The runtime plane says what `NamedTuple` does when the program runs. S3's central sentence
is NEGATIVE: the Python runtime does NOT enforce function and variable type annotations.
So the runtime meaning of `NamedTuple` is almost nothing — a `NamedTuple` subclass IS a
plain `tuple` at runtime (S4: `NamedTupleMeta` extends `tuple`'s metaclass; instances are
plain `tuple` instances constructed positionally), and field/type enforcement happens *only*
at type-check time.

### 2.1 `class X(NamedTuple)` is a tuple subclass at runtime

- **R1 (plain tuple instance).** `class Point(NamedTuple): x: int; y: int` produces, at
  runtime, a class `Point` whose instances are plain `tuple` instances. `isinstance(p,
  tuple)` is `True` for any `p: Point`. Constructing `Point(1, 2)` produces a plain tuple
  `(1, 2)`; the field names `x`, `y` are accessible via `getattr(p, "x")` and `p.x`, but
  these are tuple-index reads under the hood (`p[0]`, `p[1]`). — *cites S3
  (`typing.NamedTuple`); resolved by S4 (`NamedTupleMeta` in `Lib/typing.py`).*
- **R2 (introspection).** `typing.get_type_hints(Point)` returns `{"x": int, "y": int}`;
  `Point._fields` is `("x", "y")`; `Point._field_defaults` is `{}` (or the defaults map).
  These are introspection only — they do not enforce anything. — *cites S3; resolved by S4.*
- **R3 (no enforcement).** The runtime does NOT check that a value stored under a `Point`
  annotation has fields `x`, `y` of types `int`, `int`. Assigning a plain `(1, 2)` tuple to
  a `Point`-typed variable succeeds at runtime (it IS a tuple). A wrong-typed construction
  `Point("a", 2)` succeeds at runtime (the `str` is stored at index 0). — *cites S3 (central
  negative sentence); resolved by S4.*
- **R4 (no isinstance against NamedTuple type).** `isinstance(v, Point)` is `True` iff `v`
  is a `tuple` of the right length — `NamedTuple` subclasses define `__instancecheck__` by
  tuple-ness + length, NOT by field types (S4: the default `NamedTuple` does NOT override
  `__instancecheck__`; a `Point` instance is a `tuple` instance). This is a runtime
  tuple-shape check, not a type-enforcement check. — *cites S3; resolved by S4.*

### 2.2 Field access at runtime

- **R5 (attribute is tuple-index).** `p.x` at runtime is a plain tuple-index read
  (`p[0]`) exposed via a synthesized `property`. There is no type-check; the value returned
  is whatever was stored at that tuple position. `p.x = v` raises `AttributeError`
  (NamedTuple instances are immutable tuples). — *cites S3; resolved by S4.*
- **R6 (subscript is tuple subscript).** `p[0]` at runtime is a plain tuple subscript — it
  returns the tuple's value at index 0. There is no type-check; the value returned is
  whatever was stored. `p[0] = v` raises `TypeError` (tuples are immutable). — *cites S3;
  resolved by S4.*
- **R7 (no key/type check on subscript).** A subscript `p[2]` for an out-of-range index
  raises plain `IndexError` (the tuple's native bounds), not a NamedTuple-specific error. A
  non-integer index raises plain `TypeError`. — *cites S3; resolved by S4.*

### 2.3 Identity / shim faithfulness

- **R8 (no validation in the shim).** Any `src/pycsl_lib/typing` shim for `NamedTuple`
  must agree with S4: it exposes the introspectable class object and performs NO validation
  of annotated values. A shim that CHECKED whether a value has the declared field types
  would be unfaithful in exactly the way an over-strong axiom is. — *cites S3, S4.*
- **R9 (plain-tuple alias).** Because a NamedTuple instance IS a plain tuple, the runtime
  plane of a NamedTuple-typed value is just the plain-tuple plane (`tuple.__getitem__`,
  `len`, `getattr`-via-property). There is no separate NamedTuple runtime behaviour beyond
  the class object's introspection methods and the synthesized `property` accessors. — *cites
  S3, S4.*

---

## 3. DIVERGENCE

The two planes disagree, and the disagreement is permanent: neither plane's claim may
stand in for the other. Stating them as a single contract is the canonical
coherent-and-wrong failure (typing edition).

- **D1 (record type vs plain tuple).** The static plane (§1) treats `Point` as a record
  type with fixed-name, fixed-type fields — `p.x` is a record-field read typed `int`, `p[0]`
  is a record-field-by-index read typed `int`. The runtime plane (§2) treats `Point` as a
  plain tuple — `p.x` is a tuple-index read via a property (`p[0]`), `p[0]` is a tuple
  subscript, both returning whatever value was stored, with no type guarantee. The static
  claim "this value's `x` field is an `int`" is NOT carried by the runtime tuple; the
  runtime tuple does NOT check it.
- **D2 (arity/type enforcement).** The static plane (N6/N7) rejects constructions with
  wrong arity or wrong-typed arguments at type-check time. The runtime plane (R1/R3)
  accepts any positional construction that fits the tuple length; wrong-typed arguments are
  silently stored. NEITHER runtime behaviour is the static typing rule.
- **D3 (isinstance).** The static plane uses nominal typing (N2); `isinstance(v, Point)`
  is the runtime tuple-shape check (R4), NOT the static nominal-typing judgment. A lowering
  that let a runtime `isinstance`-or-tuple-shape check satisfy the static record-shape
  obligation would blend the planes.
- **D4 (no-blend invariant).** The static plane's obligations (§1) and the runtime plane's
  plain-tuple behaviour (§2) are carried as SEPARATE contracts, separately labelled. A
  `NamedTuple` whose runtime plain-tuple alias passes a static field-access VC is a finding
  (gap doc), not a success. The no-blend rule is defended by author separation: this
  spec-agent and the conformance-agent never read the core-agent's lowering.

---

## 4. CLASSIFICATION

- **Static plane: INTERPRETED.** `class Point(NamedTuple)` is consumed by the static plane
  and lowered to a record type declaration with one field per declared key (in declaration
  order); named field access `p.x` lowers to a record-field read; positional access `p[0]`
  lowers to a record-field read by index; construction `Point(1, 2)` lowers to a record
  literal. Each clause N2–N7 maps to one VC or one S5 conformance case. The construct is
  classified **Interpreted** in `--soundness-report`.
- **Runtime plane: SHIMMED.** The runtime meaning of `NamedTuple` is the plain-tuple
  behaviour (a NamedTuple instance IS a tuple; subscripts are tuple subscripts; attribute
  access is tuple-index-via-property; no enforcement) plus the introspectable class object.
  Any `src/pycsl_lib/typing` surface for `NamedTuple` is a thin shim that exposes the class
  object and performs no validation. The construct is classified **Shimmed** in
  `--soundness-report`.
- **Combined classification:** `NamedTuple` is **Interpreted on the static plane, Shimmed
  on the runtime plane** — both classifications apply, separately, per the no-blend rule
  (§3 of `typing-global-overview.md`).

### GT gap codes tagged in this spec

- **GT7 — runtime/static split (analogous, NOT a new code).** D3 documents the
  `isinstance`-against-NamedTuple asymmetry: the static N2 record-shape obligation must NOT
  be discharged by any runtime `isinstance`/tuple-shape check (R4 is a tuple-ness check, not
  a type-enforcement check). This is a NamedTuple-local restatement of the no-blend rule,
  tagged in the report as a `no_blend_namedtuple_isinstance` note, not a new GT code.
- **GT8 — S5 conformance subset.** The S5 subset for `NamedTuple` is not yet declared; it
  is the conformance-agent's standing artifact. Each clause N2–N7 above names the S5 case
  shape it commits to; the declared subset is built from those case shapes.

No other GT gap is tagged in this spec. GT1 (`Any`), GT2 (variance), GT3
(`ParamSpec`/`TypeVarTuple`), GT4 (polymorphic recursion), GT5 (forward-reference
resolution order, owned by TY0), and GT6 (`# type: ignore`) are out of scope for
`NamedTuple` at TY2.
