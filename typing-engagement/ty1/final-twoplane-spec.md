# `Final` (PEP 591) — Two-Plane Spec

**Status:** Two-plane spec for the `Final` construct. Authored by the typing-spec-agent
under the TY1 tier. This document carries the static claim, the runtime claim, the
divergence between them, and the Interpreted/Shimmed/Ignored classification — in four
sections that must NOT be merged. It cites the S1–S7 authorities per §3.1 of
`typing-global-impl.md` and proposes NO lowering (that is the core-agent's job); the
single mechanism named below — "degenerate HAPPY no-write confinement" — is named only
to confirm each static clause is dischargeable by SOME mechanism, never to prescribe
syntax. Each static obligation clause is stated so it maps to one VC or one S5
conformance case; each runtime claim is checked against S3's negative sentence
(annotations are not enforced) resolved by S4. `Final` is fully sound — the
write-restriction is decidable (a syntactic write-site check) — so NO GT gap is tagged
for it in this spec.

**Authorities cited in this spec:**
- **S1** — the typing specification (typing.readthedocs.io, Typing Council / PEP 729).
  S1 defines `Final` semantics as a write-restriction, not a type refinement.
- **S2** — PEP 591 (defining PEP for `Final`). S1 supersedes S2 on any conflict.
- **S3** — the library reference (`docs.python.org/3/library/typing.html`); central
  sentence is NEGATIVE: the runtime does not enforce annotations.
- **S4** — CPython `Lib/typing.py` observable behaviour (the runtime lower bound).
- **S5** — the typing conformance test suite (static executable ground truth).
- **S7** — PyCSL front-end current behaviour (TY0 baseline; see VERDICTS.md).

---

## 1. STATIC PLANE

The static plane treats `Final[T]` as a **write-restriction annotation**: the type of a
`Final[T]`-annotated name is `T` (F3 — no narrowing); what `Final` adds is a syntactic
prohibition on subsequent writes. The static meaning is a set of *judgments about programs*
— single-assignment for module/class-level names, `__init__`-only writes for instance
attributes, no type refinement — each stated below as an obligation clause precise enough
to map to one VC or one S5 conformance case. Nothing in this section claims anything
happens at runtime; runtime claims live in §2.

### 1.1 Module/class-level Final (write-once)

- **F1 (module/class-level Final — write exactly once at the declaration site).** A
  name annotated `x: Final[T] = v` at module scope or class scope may be assigned
  EXACTLY ONCE: at its declaration. Any subsequent assignment to `x` — anywhere in the
  module, after the declaration — is a static error. The static obligation is: *at most
  one write to `x`, occurring at the declaration site*. This is the load-bearing
  clause: it lowers, by the named "degenerate HAPPY no-write confinement" mechanism
  (§1.4), to a check that no assignment to `x` exists outside its declaration. — *cites
  S1, PEP 591 (S2).* Two S5 conformance cases pin it: (a) a single declaration
  assignment with no further writes (accept); (b) a declaration followed by a later
  reassignment of the same name (reject).

### 1.2 Instance attribute Final (__init__-only writes)

- **F2 (instance attribute Final — writes ONLY in the class's own __init__).** An
  instance attribute annotated `attr: Final[T]` declared in class `C`'s body may be
  written ONLY inside `C`'s own `__init__` method (the class that declares the
  attribute). Every write to `self.attr` outside `C.__init__` — in other methods of
  `C`, in subclasses' `__init__`, or anywhere else — is a static error. Reads of
  `self.attr` are unrestricted. The static obligation is: *every write to `self.attr`
  occurs textually inside `C.__init__`*, where `C` is the class declaring the attribute.
  This is the load-bearing clause for the attribute form: it lowers, by the named
  "degenerate HAPPY no-write confinement" mechanism (§1.4), to a check that no write
  site for `self.attr` exists outside `C.__init__`. — *cites S1, PEP 591 (S2).* Three
  S5 conformance cases pin it: (a) a write to `self.attr` inside `C.__init__` (accept);
  (b) a write to `self.attr` in a method of `C` other than `__init__` (reject); (c) a
  write to `self.attr` in a subclass's `__init__` (reject).
- **F2a (declaration is not a write for instance attributes).** The class-body line
  `attr: Final[T]` (with no `= value`) is a declaration, NOT a write — it establishes
  the attribute's existence and its `Final` write-policy, and the first (and only
  permitted) write happens in `__init__`. A class-body line `attr: Final[T] = v` with
  an initializer IS a write and must occur in `__init__` (or be a class-level `Final`
  per F1, depending on whether it is `self.attr`-bound). — *cites S1, PEP 591 (S2).*
- **F2b (subclass cannot widen the write-perimeter).** A subclass `D(C)` inherits the
  `Final` attribute with the SAME write-perimeter: writes to `self.attr` in `D.__init__`
  or any `D` method are still a static error, because the attribute's `Final` policy is
  owned by `C`. — *cites S1, PEP 591 (S2).* One S5 case: write to `self.attr` in
  `D.__init__` where `D(C)` and `attr: Final[T]` is declared in `C` (reject).

### 1.3 No narrowing

- **F3 (Final does not narrow or refine the type).** `x: Final[int]` has the static
  type `int`, not a refined or singleton type. `Final` adds the write-restriction (F1
  or F2); it does NOT add a value-set refinement, a narrowing fact, or an assignability
  refinement. A `Final[T]`-typed expression is assignable to `T` and vice versa without
  any narrowing obligation. The static obligation here is the *absence* of a
  narrowing claim: the type checker must not treat `x: Final[int] = 5` as narrowing
  `x`'s type to `Literal[5]` (that would be a blend with constant inference, a separate
  concern). — *cites S1, PEP 591 (S2) §"Final does not change the type".* One S5 case:
  a `Final[int]`-typed name used where `int` is expected typechecks (accept), with no
  narrowing obligation emitted.

### 1.4 Expressibility check (dischargeability, NOT a lowering proposal)

Each clause above is stated so it can be discharged by SOME mechanism: the "degenerate
HAPPY no-write confinement" mechanism — i.e. HAPPY's per-attribute no-write policy,
scoped to a single attribute and a single allowed writer (the declaration site for F1,
`C.__init__` for F2) — makes the write-restriction a syntactic write-site check that
is decidable by construction (a write either is or is not textually inside the allowed
perimeter). F1 becomes a single write-site check (no assignment to the name after its
declaration); F2 becomes a per-attribute write-site check (every write to `self.attr`
is textually inside `C.__init__`); F2b extends the check across the inheritance graph
(the perimeter is fixed by the declaring class); F3 is the absence of any narrowing
obligation (a check that no narrowing VC was emitted). The spec-agent confirms each
clause is dischargeable by this mechanism; the mechanism was named in
`typing-global-impl.md` §5 / §0 ("Final as degenerate HAPPY") and the overview §4.2
(TY1 "Final/ClassVar → a no-write-outside-__init__ degenerate HAPPY-style
meta-property"), and `Final` introduces NO new mechanism — it reuses HAPPY's existing
no-write confinement in a single-attribute, single-writer degenerate form. Because the
write-restriction is a syntactic check (decidable: a write site either is or is not
inside the allowed perimeter), `Final` is fully sound — no GT gap applies.

### 1.5 The HAPPY reuse (named, not proposed)

- **F4 (the lowering reuses HAPPY — named mechanism, NOT a lowering proposal).** The
  no-write-outside-`__init__` check that discharges F1/F2 is a **degenerate form of
  HAPPY's no-write confinement**: HAPPY's per-attribute write policy (the meta-pass that
  enforces "no attribute is written outside its allowed writer-set"), scoped to a single
  attribute and a single allowed writer (the declaration site for module/class-level
  `Final`, the declaring class's `__init__` for instance-attribute `Final`). The
  reuse is structural: HAPPY already implements no-write confinement; `Final` is the
  single-attribute, single-writer special case. This clause NAMES the reuse (so the
  spec is dischargeable); it does NOT prescribe how the core-agent wires it (syntax,
  IR node, meta-pass invocation). — *cites `typing-global-impl.md` §0/§5; overview
  §4.2 (TY1).*

---

## 2. RUNTIME PLANE

The runtime plane says what `Final` does when the program runs. S3's central sentence
is NEGATIVE: the Python runtime does NOT enforce function and variable type
annotations. So the runtime meaning of `Final` is almost nothing — it is an
introspectable alias object, not a check.

### 2.1 `Final[T]` is a runtime alias object, not a check

- **FR1 (alias object identity).** `Final[T]` evaluates to an instance of
  `typing.Final` (or, in modern CPython, an object whose `__origin__` /
  `__class_getitem__` machinery yields the `Final` alias). It is a plain
  introspectable alias object; it is NOT a distinct runtime type and NOT a write-guard.
  — *cites S3 (`typing.Final`); resolved by S4 (`Lib/typing.py`'s `_SpecialForm` /
  `_Final`).*
- **FR2 (introspection).** `typing.get_origin(Final[int])` returns `typing.Final`;
  `typing.get_args(Final[int])` returns `(int,)`. The annotated type appears as itself
  in the args. — *cites S3; resolved by S4.*
- **FR3 (no enforcement of the write-restriction).** The runtime does NOT check that
  a name annotated `Final[T]` is written only once or that an attribute annotated
  `Final[T]` is written only in `__init__`. Reassigning a `Final` name at runtime
  SUCCEEDS (no error): the assignment executes, the name is rebound, and no exception
  is raised. The write-once / `__init__`-only restriction is a static-plane judgment
  ONLY. — *cites S3 (central negative sentence).*

### 2.2 `Final` and `isinstance`

- **FR4 (`isinstance` against `Final`).** `isinstance(v, Final[int])` raises
  `TypeError` at runtime — `typing.Final` aliases are not valid second arguments to
  `isinstance`. The runtime has no membership test for `Final`-ness (which would be
  meaningless anyway, since `Final` is a write-restriction, not a value property). —
  *cites S3; resolved by S4.*

### 2.3 Identity / shim faithfulness

- **FR5 (no validation in the shim).** Any `src/pycsl_lib/typing` shim for `Final`
  must agree with S4: it constructs the introspectable alias object and performs no
  validation of writes to `Final`-annotated names. A shim that CHECKED whether a write
  occurs outside `__init__` (or anywhere) would be unfaithful in exactly the way an
  over-strong axiom is. — *cites S3, S4.*
- **FR6 (`Final` is not a distinct runtime class).** A faithful shim does NOT introduce
  a distinct `Final` runtime class, a write-guard descriptor, or any runtime
  enforcement hook; `Final[T]` must be the `typing.Final` alias object, per FR1.
  Introducing a descriptor that raised on a second write would blend the planes (see
  §3) and diverge from S4. — *cites S3, S4.*

---

## 3. DIVERGENCE

The two planes disagree, and the disagreement is permanent: neither plane's claim may
stand in for the other. Stating them as a single contract is the canonical
coherent-and-wrong failure (typing edition). The `Final` divergence is the
write-restriction-vs-no-enforcement specialization of the same shape as the
ground-requires-vs-alias-object split (cf. `Literal` LD1) — sharpened because the
static plane here restricts *writes* (not values), so the temptation is to "enforce"
the static write-policy at runtime via a descriptor, which is exactly the blend to
refuse.

- **FD1 (static write-restriction vs runtime no-enforcement).** The static plane (§1)
  treats `Final[T]` as a write-restriction: write-once at the declaration (F1) or
  `__init__`-only for instance attributes (F2), with no type narrowing (F3). The
  runtime plane (§2) treats it as an introspectable `typing.Final` alias object that
  enforces nothing (FR1–FR6). The static claim "this name may be written only once"
  (or "this attribute may be written only in `__init__`") is NOT carried by the
  runtime alias object; the alias object does NOT check it. A program that reassigns a
  `Final` name is a **static error but runs fine at runtime** — the reassignment
  executes, the name is rebound, no exception is raised. This is the load-bearing
  `Final` divergence: the static write-restriction and the runtime no-enforcement are
  DIFFERENT THINGS, carried as separate contracts.
- **FD2 (no-blend — the runtime must not "pass" the static write-restriction).** The
  static plane's write-policy check (F1/F2) is a proof-time / static-analysis
  judgment: it asks "is there a write site outside the allowed perimeter?" — a
  syntactic property of the program, discharged independently of any execution. The
  runtime plane's no-enforcement (FR3) means a write at runtime succeeds. A lowering
  that let the runtime success of a write SATISFY the static write-policy check would
  blend the planes: the static VC is the write-policy check (does a disallowed write
  site exist?), independent of runtime behaviour. Conversely, a shim that introduced a
  runtime descriptor raising on a second write (FR6) would encode the static
  write-policy into the runtime, which is the canonical coherent-and-wrong failure for
  `Final`. The no-blend rule: the static write-policy is checked statically; the
  runtime does not enforce it; these are separate.
- **FD3 (no-blend invariant).** The static plane's obligations (§1) and the runtime
  plane's alias-object/no-enforcement behaviour (§2) are carried as SEPARATE contracts,
  separately labelled. A `Final` whose runtime shim passes a static conformance case
  (e.g. a descriptor that raises on a second write making the "reassignment is an
  error" case pass at runtime) is a finding (gap doc), not a success. The no-blend
  rule is defended by author separation: this spec-agent and the conformance-agent
  never read the core-agent's lowering. Specialization of the Literal LD3 / Union D4
  no-blend rule.

---

## 4. CLASSIFICATION

- **Static plane: INTERPRETED (via degenerate HAPPY no-write confinement).** `Final[T]`
  is consumed by the static plane and lowered — through the named "degenerate HAPPY
  no-write confinement" mechanism, with no new mechanism — to obligations:
  write-once-at-declaration for module/class-level names (F1), `__init__`-only writes
  for instance attributes (F2/F2a/F2b), and the absence of narrowing (F3). Each clause
  maps to one VC or one S5 conformance case, discharged by the HAPPY no-write
  confinement in its single-attribute, single-writer degenerate form (F4). The
  construct is classified **Interpreted** in `--soundness-report`.
- **Runtime plane: SHIMMED.** The runtime meaning of `Final[T]` is the introspectable
  `typing.Final` alias object with no enforcement (FR1–FR6). Any
  `src/pycsl_lib/typing` surface for `Final` is a thin shim that constructs the alias
  object and performs no validation, introducing no distinct `Final` class and no
  write-guard descriptor (FR6). The construct is classified **Shimmed** in
  `--soundness-report`.
- **Combined classification:** `Final` is **Interpreted on the static plane, Shimmed
  on the runtime plane** — both classifications apply, separately, per the no-blend
  rule (§0/§3 of `typing-global-impl.md`). This is structurally identical to the
  `Literal` / Union / Optional classification, but the static mechanism is different
  (degenerate HAPPY no-write confinement, not the ground-requires disjunction or the
  sum-type variant) — which is the point: `Final` is a write-restriction, discharged
  by reusing HAPPY's existing no-write meta-pass in a degenerate single-attribute
  form, not by a value-set or constructor obligation.

### GT gap codes tagged in this spec

No GT gap is tagged for `Final`. `Final` is fully sound: the write-restriction is a
syntactic write-site check — a write either is or is not textually inside the allowed
perimeter (the declaration for F1, the declaring class's `__init__` for F2) — and is
therefore decidable by construction. There is no `Any`-style gradual-consistency
concern (the write-policy does not consult the value's type), no variance (monomorphic,
no TypeVars), no `ParamSpec`/`TypeVarTuple`, no polymorphic recursion, no
forward-reference order beyond what TY0 owns, no `# type: ignore`, and no
runtime/static `Protocol`-style split. The no-blend discipline (FD2 — the runtime
must not "pass" the static write-restriction, and the shim must not introduce a
descriptor that enforces it) is restated here as a `Final`-local specialization of
the Literal LD2 / Union D2 no-blend rule, NOT as a new GT code. It is the load-bearing
`Final`-local restatement because the write-restriction is THE obligation for
`Final`, so the temptation to enforce it at runtime is greatest here.
