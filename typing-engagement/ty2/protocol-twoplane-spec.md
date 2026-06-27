# `Protocol` (PEP 544) — Two-Plane Spec

**Status:** Two-plane spec for the `Protocol` construct. Authored by the typing-spec-agent
under the TY2 tier. This document carries the static claim, the runtime claim, the
divergence between them, and the Interpreted/Shimmed/Ignored classification — in four
sections that must NOT be merged. It cites the S1–S7 authorities per §3.1 of
`typing-global-impl.md` and proposes NO lowering (that is the core-agent's job). Each
static obligation clause is stated so it maps to one VC or one S5 conformance case; each
runtime claim is checked against S3's negative sentence (annotations are not enforced)
resolved by S4. The GT7 no-blend trap is sharpest here — the canonical
`@runtime_checkable Protocol` presence-vs-conformance split — and is tagged explicitly in
§3.

**Authorities cited in this spec:**
- **S1** — the typing specification (typing.readthedocs.io, Typing Council / PEP 729).
  PEP 544 (S2) is the defining PEP; the typing spec's "Protocols" / "Structural
  subtyping" sections are authoritative. Where S1 and PEP 544 conflict, S1 wins.
- **S2** — PEP 544 (Protocols: Structural subtyping, static and runtime) introduces
  `Protocol` as a base class marking a protocol class, `@runtime_checkable` as the
  decorator that opts a protocol into `isinstance`/`issubclass` support, and the
  `runtime_checkable` presence-only semantics. PEP 544 §"Runtime Checking of
  Protocols" is explicit: `isinstance` against a `@runtime_checkable` protocol checks
  attribute PRESENCE only, "not type signatures, not types of attributes, [not]
  except [...] side-effects of attributes."
- **S3** — the library reference (`docs.python.org/3/library/typing.html#typing.Protocol`
  and `#typing.runtime_checkable`); central sentence is NEGATIVE: the runtime does not
  enforce annotations. For `@runtime_checkable` the library reference restates PEP 544's
  presence-only semantics and warns it is unsound for type-checking purposes.
- **S4** — CPython `Lib/typing.py` observable behaviour (the runtime lower bound):
  `@runtime_checkable` sets the protocol's `_is_runtime_protocol = True` and installs an
  `__instancecheck__` that, for each protocol member name, tests `hasattr(obj, name)`
  only (S4: `_get_protocol_attrs` collects the member names; `__instancecheck__` is a
  `hasattr` loop — `Lib/typing.py:_runtime_checkable_wrapper`). No signature, contract,
  or attribute-type check occurs.
- **S5** — the typing conformance test suite (static executable ground truth).
- **S7** — PyCSL front-end current behaviour (TY0 baseline): a `class X(Protocol)`
  declaration is currently parsed as a *regular* `ast.ClassDef` whose `bases` contains
  `Protocol`; `_collect_class_fields` returns an *empty* record (Protocol method
  declarations carry no `__init__` assigns and are `FunctionDef`s, not `AnnAssign`s).
  `@runtime_checkable` is recorded as a plain decorator with NO static-plane effect.
  The protocol methods are emitted as regular function IR nodes. There is currently NO
  protocol-interface synthesis and NO conformance checking — this is the unspec'd de-facto
  behaviour TY0 must pin.

---

## 1. STATIC PLANE

The static plane treats `class P(Protocol)` as a **contract interface**: a named set of
method signatures, each carrying a contract (pre/post/frame). A class `C` **conforms to**
`P` iff, for every method `m` declared in `P`, `C` has a matching method `m` whose
signature is compatible AND whose contract **refines** `P.m`'s contract (weaker
precondition, stronger postcondition, narrower frame). This is full-signature
behavioural refinement — NOT attribute presence. The static meaning is a set of
*judgments about programs* — protocol-interface declaration, conformance, the
non-conformance rejection, and the no-blend rule against the runtime presence check —
each stated below as an obligation clause precise enough to map to one VC or one S5
conformance case. Nothing in this section claims anything happens at runtime; runtime
claims live in §2.

### 1.0 Syntax forms (PEP 544)

- **P1 (protocol class declaration).** `class P(Protocol): ...` declares a protocol type
  named `P`. A protocol class is recognized by the bare head name `Protocol` (or a dotted
  `typing.Protocol`) in `node.bases`. The class body declares one or more method
  signatures (each a `def` with `...` body by convention, though PEP 544 permits real
  bodies) — these are the protocol's *members*. — *cites S1, PEP 544 (S2).*
- **P1a (protocol members).** Each `def m(self, ...) -> R: ...` in a `Protocol` body is a
  protocol **member**: a method signature that conforming classes must provide. A member
  may carry a `#@ ensures Q` / `#@ requires R` / `#@ assigns A` contract; this contract
  is the refinement TARGET — conforming classes' `m` must refine it. — *cites S1, PEP 544
  (S2).* One S5 case per member-with-a-contract: a conforming class's method refines the
  member's contract; one reject case: a non-refining method.
- **P1b (`@runtime_checkable` is a SEPARATE marker, NOT a static modifier).**
  `@runtime_checkable` decorates a protocol class to make it usable as the second argument
  of `isinstance`/`issubclass` at runtime. It has NO static-plane effect: a
  non-`@runtime_checkable` protocol has the SAME static conformance semantics as a
  `@runtime_checkable` one. The static plane ignores `@runtime_checkable` (it is a
  runtime-plane concern, §2). — *cites S1, PEP 544 (S2).*

### 1.1 Conformance (the load-bearing static rule)

- **P2 (per-method behavioural refinement, the load-bearing rule).** A class `C`
  **conforms to** protocol `P` iff, for every member `m` of `P`, `C` has a method `m`
  such that:
  (a) the signatures are compatible (same name, compatible parameter types, compatible
      return type — structural subtyping, PEP 544 §"Subtyping Relationships"); AND
  (b) `C.m`'s contract **refines** `P.m`'s contract: `requires(C.m) ⟹ requires(P.m)`
      (weaker-or-equal pre: a caller safe under `P.m`'s pre is safe under `C.m`),
      `ensures(P.m) ⟹ ensures(C.m)` (stronger-or-equal post: `C.m` establishes at least
      what `P.m` promises), `assigns(C.m) ⊆ assigns(P.m)` (narrower frame).
  — *cites S1, PEP 544 (S2).* This is the FULL-SIGNATURE BEHAVIOURAL REFINEMENT
  obligation. One VC per conforming member (the refinement VC); one S5 accept case (a
  conforming class) and one reject case (a non-conforming class).
- **P3 (non-conformance is a static error).** A class `C` that lacks a member of `P`, or
  whose member's contract does NOT refine `P.m`'s contract, does NOT conform to `P`. A
  program that treats such a `C` value as a `P` (e.g. passing `c: C` where `P` is
  expected) is a static type error. — *cites S1, PEP 544 (S2).* One S5 reject case.
- **P4 (the conformance obligation is a per-method VC, NOT a presence check).** The
  conformance judgment P2 is discharged by a **per-method contract-refinement VC**: for
  each `P.m`, prove `C.m`'s contract refines `P.m`'s contract. It must NOT be discharged
  by checking that `C` has an attribute named `m` (that is the runtime plane, R3). A
  lowering that let attribute presence satisfy the static conformance obligation would
  blend the planes. — *cites S1; the no-blend rule (§0 of `typing-global-impl.md`), GT7.*
  One S5 case: a class with method presence but a NON-refining contract FAILS conformance
  (this is the keystone no-blend witness — see §3 D1).

### 1.2 The no-blend rule (static side)

- **P5 (conformance is contract refinement, NOT attribute presence).** The static
  conformance obligation (P2/P4) is discharged by a **per-method contract-refinement
  VC**. It must NOT be discharged by any runtime `isinstance` or `hasattr` check. The
  runtime `@runtime_checkable` isinstance (R3) checks attribute PRESENCE only — it is a
  value check on the object, NOT the type judgment. The two are carried as SEPARATE
  facts: the static conformance VC is discharged by contract refinement; the runtime
  isinstance is discharged by the object's attribute presence at run time. — *cites S1,
  PEP 544 (S2); the no-blend rule (§0 of `typing-global-impl.md`), GT7.* One S5 case: a
  class with attribute presence (passes runtime isinstance) but a non-refining contract
  FAILS static conformance — the load-bearing no-blend witness.

### 1.3 Expressibility check (dischargeability, NOT a lowering proposal)

Each clause above is stated so that it can be discharged by SOME mechanism the core-agent
may choose: a protocol class synthesizes a contract interface (a named collection of
method contracts); conformance is checked per-method — for each `P.m`, the conformance VC
is `requires(C.m) ⟹ requires(P.m) ∧ ensures(P.m) ⟹ ensures(C.m) ∧ assigns(C.m) ⊆
assigns(P.m)`, a Why3 implication over contracts (the existing `==>` implication
operator, lowered to WhyML `->`, supports implication-in-requires/ensures natively). The
member's contract is the refinement TARGET (a WhyML `ensures`/`requires` formula over the
method's parameters and `\result`); `C.m`'s contract is the refinement SOURCE. The VC is
discharged by Why3/SMT from the two contract formulas — no body execution required (this
is contract refinement, not implementation proof). The spec-agent confirms each clause is
dischargeable by some such mechanism; the choice of mechanism is the core-agent's, not
this spec's. **The core-agent's hard rule (`typing-global-impl.md` §5, TY2): `Protocol`
is a contract interface, conformance as per-method behavioural refinement. NO `\trusted`.**

---

## 2. RUNTIME PLANE

The runtime plane says what `Protocol` does when the program runs. S3's central sentence
is NEGATIVE: the Python runtime does NOT enforce function and variable type annotations.
For `Protocol` the runtime meaning is almost nothing UNLESS the protocol is decorated
`@runtime_checkable` — in which case `isinstance`/`issubclass` against the protocol
checks attribute PRESENCE ONLY (S3/S4), never signature, never contract, never attribute
type.

### 2.1 `class X(Protocol)` is a plain class at runtime

- **R1 (plain class).** `class P(Protocol): ...` produces, at runtime, a plain class `P`
  whose metaclass is `_ProtocolMeta` (a subclass of `ABCMeta`). Instances of `P` are
  plain instances; the `Protocol` base contributes the `__init_subclass__` hook that
  records the protocol's members but performs NO type enforcement. — *cites S3
  (`typing.Protocol`); resolved by S4 (`Lib/typing.py:_ProtocolMeta`).*
- **R2 (no isinstance by default).** For a protocol that is NOT `@runtime_checkable`,
  `isinstance(x, P)` RAISES `TypeError` at runtime — protocols are not usable as
  `isinstance` second arguments unless explicitly opted in. — *cites S3; resolved by S4
  (`_ProtocolMeta.__instancecheck__` raises `TypeError('Protocols can only use
  @runtime_checkable for isinstance')`).*
- **R3 (runtime_checkable isinstance is PRESENCE-ONLY — the load-bearing runtime rule).**
  For a `@runtime_checkable` protocol `P`, `isinstance(x, P)` returns `True` iff, for
  every member name `m` of `P`, `hasattr(x, m)` is `True`. It checks attribute PRESENCE
  ONLY — it does NOT check the member's signature (parameter types, return type), it does
  NOT check the member's contract (pre/post/frame), it does NOT check attribute types.
  PEP 544 and S3 are explicit that this is unsound for type-checking. — *cites S3
  (`typing.runtime_checkable`); resolved by S4 (`_runtime_checkable_wrapper` — a
  `hasattr` loop over `_get_protocol_attrs`).*

### 2.2 Identity / shim faithfulness

- **R4 (no validation in the shim).** Any `src/pycsl_lib/typing` shim for
  `runtime_checkable` must agree with S4: it returns the class unchanged and performs NO
  signature check, NO contract check, NO attribute-type check. A shim that CHECKED
  whether an object conforms to the protocol's full signature would be unfaithful in
  exactly the way an over-strong axiom is. — *cites S3, S4.*
- **R5 (isinstance result is a plain bool).** The `isinstance(x, P)` call (when
  `P` is `@runtime_checkable`) returns a plain Python bool — `True` if every member name
  is present, `False` otherwise. There is no "partial conformance"; the check is
  all-or-nothing over attribute presence. — *cites S3, S4.*
- **R6 (no static conformance at runtime).** The runtime does NOT perform the static
  conformance check (P2). A value that fails static conformance (e.g. its `m` has a
  non-refining contract) but has all member attributes PRESENT will PASS `isinstance(x,
  P)` at runtime. This is the runtime-side restatement of the no-blend rule (P5). — *cites
  S3, S4.*
- **R7 (the protocol class is a plain class).** The runtime plane of a protocol class
  (beyond `@runtime_checkable`) is the plain-class plane — there is no separate protocol
  runtime behaviour beyond the presence-only isinstance when opted in. — *cites S3, S4.*

---

## 3. DIVERGENCE

The two planes disagree, and the disagreement is permanent: neither plane's claim may
stand in for the other. Stating them as a single contract is the canonical
coherent-and-wrong failure (typing edition), and for `Protocol` the trap is the SHARPEST
in the whole engagement (§5 of `typing-global-impl.md` flags it explicitly).

- **D1 (full-signature refinement vs presence-only isinstance — THE GT7 CANONICAL TRAP).**
  The static plane (§1) judges conformance as FULL-SIGNATURE BEHAVIOURAL REFINEMENT
  (P2/P4): each `P.m`'s contract must be refined by `C.m`'s contract. The runtime plane
  (§2) judges conformance (when `@runtime_checkable`) as ATTRIBUTE PRESENCE ONLY (R3):
  `hasattr(x, m)` for each member name. The two are DIFFERENT judgments with DIFFERENT
  outcomes: a class `C` can PASS the runtime isinstance (all members present) while
  FAILING static conformance (a member's contract does not refine `P.m`'s). A lowering
  that let the weak runtime presence check SATISFY the static full-signature conformance
  obligation would blend the planes — this is the GT7 canonical failure. The two are
  carried as SEPARATE facts: the static conformance VC is a contract-refinement formula
  (discharged by Why3/SMT over the two contracts); the runtime isinstance is a `hasattr`
  loop (discharged by the object's attribute presence at run time).
- **D2 (the non-`@runtime_checkable` asymmetry).** A non-`@runtime_checkable` protocol
  has the SAME static conformance semantics (P1b — `@runtime_checkable` is not a static
  modifier) but NO runtime isinstance support (R2 raises `TypeError`). The static plane
  is unaffected by the runtime decorator; the runtime plane is gated by it. Neither
  plane's claim stands in for the other.
- **D3 (no-blend invariant).** The static plane's obligations (§1) and the runtime
  plane's presence-only behaviour (§2) are carried as SEPARATE contracts, separately
  labelled. A `Protocol` whose `@runtime_checkable` isinstance passes the static
  conformance VC is a finding (gap doc), not a success — because the static VC must be
  discharged by per-method contract refinement, independent of the runtime presence
  check. The no-blend rule is defended by author separation: this spec-agent and the
  conformance-agent never read the core-agent's lowering.

---

## 4. CLASSIFICATION

- **Static plane: INTERPRETED.** `class P(Protocol)` is consumed by the static plane and
  lowered to a contract interface (a named collection of method contracts); conformance
  `C conforms to P` is checked per-method as a contract-refinement VC (P2/P4). Each
  clause P2–P5 maps to one VC or one S5 conformance case. The construct is classified
  **Interpreted** in `--soundness-report`.
- **Runtime plane: SHIMMED.** The runtime meaning of `Protocol` is the plain-class
  behaviour plus, when `@runtime_checkable`, the presence-only `isinstance` (a `hasattr`
  loop over member names). Any `src/pycsl_lib/typing` surface for `runtime_checkable` is
  a thin shim that returns the class unchanged and performs no validation. The construct
  is classified **Shimmed** in `--soundness-report`.
- **Combined classification:** `Protocol` is **Interpreted on the static plane, Shimmed
  on the runtime plane** — both classifications apply, separately, per the no-blend rule
  (§3 of `typing-global-overview.md`).

### GT gap codes tagged in this spec

- **GT7 — the canonical runtime/static Protocol split (this IS the GT7 trap, not an
  analogue).** D1 documents the `@runtime_checkable` presence-vs-conformance
  divergence: the static P2/P4 full-signature behavioural-refinement obligation must NOT
  be discharged by any runtime `isinstance`/`hasattr` presence check (R3 is attribute
  presence, a value check, NOT the contract-refinement type judgment). This is THE GT7
  trap named in §5 of `typing-global-impl.md` ("the Protocol runtime/static split"),
  tagged in the report as a `no_blend_protocol_presence` note.
- **GT8 — S5 conformance subset.** The S5 subset for `Protocol` is not yet declared; it
  is the conformance-agent's standing artifact. Each clause P2–P5 above names the S5 case
  shape it commits to; the declared subset is built from those case shapes.

No other GT gap is tagged in this spec. GT1 (`Any`), GT2 (variance), GT3
(`ParamSpec`/`TypeVarTuple`), GT4 (polymorphic recursion), GT5 (forward-reference
resolution order, owned by TY0), and GT6 (`# type: ignore`) are out of scope for
`Protocol` at TY2. Generic protocols (`Protocol[T]`) are TY3 (the monomorphic TY2 scope
uses only non-generic protocols).
