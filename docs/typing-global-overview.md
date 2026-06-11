# `typing` Global Overview — Sources of Truth, the Two-Plane Squeeze, Parser Control, and Whole-Module Monomorphization

**Status:** Pre-normative overview. This document fixes the strategy and the
stable taxonomy (TY0–TY3, GT-gap codes) for bringing the `typing` language into
PyCSL. Each construct graduates to Normative only when its grammar production,
well-formedness rules, and lowering rules land in the three reference documents,
its corpus prove/fail pair exists, and `bin/doc-coherency.py --check` passes.
Until then, every syntax and lowering sketch here is a design commitment, not a
grammar production.
**Version:** 0.1
**Source of truth:** for the strategy, this document; for each construct, the
external authorities enumerated in §1 — never this overview alone.
**Scope:** the whole picture: where `typing`'s normative meaning lives, how the
source-of-truth squeeze changes shape for a library whose semantics are split
between a static plane and a runtime plane, why owning the parser
(`src/pycsl/frontend/pure_ast.py`) makes the static plane governable, and how
generics are discharged by whole-module monomorphization across three tiers. It
does NOT define grammar productions, error codes, or WhyML emission rules —
those are per-construct deliverables of the tiers.
**Companion documents:** `docs/pycsl-concrete-syntax-reference.md`,
`docs/pycsl-static-semantics-reference.md`,
`docs/pycsl-translational-reference.md` (the §T lowering sections each tier must
add); `test-suite/annotations.md` (canonical directive entries);
`src/pycsl/frontend/pure_ast.py` (COVERAGE MANIFEST); the soundness-report
taxonomy (Modelled / Specified / Stubbed / Confinement), which §2.3 extends.

---

## 0. The one-sentence thesis

`os` was a library whose meaning lives at the value level, so it was modelled in
`pure_lib` and crowned with formal tests; `typing` is Python's native
*specification sub-language* — its meaning lives in static judgments about
programs, which is the IR's domain — so it is **absorbed into PyCSL's
specification layer** (front-end + static semantics + Module 6 lowering), with
only a thin `pure_lib/typing` shim for the few functions that the library
reference gives genuine runtime behaviour. The proportions of the `os` effort
invert: roughly 15% shim, 85% front-end/IR/Module 6.

A bootstrap fact makes this concrete: PyCSL already interprets a fragment of
`typing` implicitly — every `def sys_write(self, fd: int, buf: bytes) -> int`
in `pure_lib/os` is the front-end and Module 6's type inference reading
annotations into IR and WhyML types. The first deliverable of this whole effort
is therefore not a feature: it is the **specification of that existing implicit
subset** (TY0, §4.2), with error codes and citations, so the verifier does not
continue to carry an unspecified interpreter inside it.

---

## 1. Sources of truth

`typing` has more than one normative authority, and they govern *different
planes* of meaning. Every rule this effort adds must `# cite:` the right one.

| # | Authority | Governs | Cited by |
|---|-----------|---------|----------|
| S1 | **The Specification for the Python type system** (typing.readthedocs.io, maintained under the Typing Council, PEP 729) | the static meaning of every typing construct: assignability, narrowing, Protocol conformance, overload resolution, generics | static-semantics rules; conformance obligations |
| S2 | **The defining PEPs** — 483 (theory), 484 (hints), 526 (variable annotations), 544 (`Protocol`), 586 (`Literal`), 589 (`TypedDict`), 591 (`Final`), 593 (`Annotated`), 604 (`X \| Y`), 612 (`ParamSpec`), 646 (`TypeVarTuple`), 673 (`Self`), 695 (type-parameter syntax), 742 (`TypeIs`) | historical rationale and the construct-level fine print; **where S1 and a PEP conflict, S1 wins** (the spec supersedes the PEPs as the living authority) | `# cite:_note:` rationale anchors |
| S3 | **The library reference** (`docs.python.org/3/library/typing.html`) | the **runtime** surface only: "the Python runtime does not enforce function and variable type annotations"; `cast(t, v)` returns `v` unchanged; `@overload` bodies are discarded; `get_origin`/`get_args` introspection | the `pure_lib/typing` shim contracts |
| S4 | **CPython's `Lib/typing.py` observable behaviour** | the runtime lower bound the shim must be faithful to (what actually executes — including what is *not* checked) | shim faithfulness audits |
| S5 | **The typing conformance test suite** (`python/typing` repository) | executable ground truth for checker behaviour; PyCSL declares the subset it conforms to and runs it as a gate (§2.4) | the conformance gate |
| S6 | **The CPython 3.12 grammar / ASDL schema** | the concrete syntax of annotations and PEP 695 forms; already the source of truth `pure_ast.py` is differentially tested against | `pure_ast` parser productions |
| S7 | **The current front-end behaviour** (`pure_ast.py`, `ir_resolve.py`, Module 6 TypeInference) | the de facto interpreted subset (TY0) — a source of truth about *PyCSL itself* that must be transcribed into the references before anything is added | the TY0 specification |

The citation discipline follows the project rule: a static-semantics rule cites
S1/S2, a shim contract cites S3 (resolved against S4 where S3 is silent), a
parser production cites S6. A rule with no citation is a defect.

---

## 2. The new squeeze strategy: two planes, two squeezes

For `os`, the squeeze was one-dimensional: the library reference bounded each
contract from above, the faithful runtime model bounded it from below, both at
the value level. `typing` splits into **two planes with independent squeezes**,
and the cardinal rule is that they must never be blended.

### 2.1 The static-plane squeeze

- **Upper bound:** S1 (the typing spec) — the strongest static judgment the
  spec justifies for a construct. PyCSL must not claim a narrowing, a
  conformance, or an assignability the spec does not license.
- **Lower bound:** what PyCSL's IR and WhyML emission can *faithfully and
  soundly* express. This bound is unusual: it is allowed to be **stricter**
  than S1, never weaker. Where the type system is deliberately unsound —
  `Any`'s consistency relation, `# type: ignore`, variance loopholes — PyCSL
  refuses to import the unsoundness. Divergence-by-strictness is recorded and
  legitimate; divergence-by-weakness is a bug. (`Any` is the canonical case:
  it launders any value into any type by design; in PyCSL it is treated like a
  trust boundary — see GT1.)

### 2.2 The runtime-plane squeeze

- **Upper bound:** S3 — and S3's central normative sentence is a *negative*
  one: the runtime does not enforce annotations. The shim must not check what
  CPython does not check; a `cast` that validated its argument would be
  unfaithful in exactly the way an over-strong axiom is.
- **Lower bound:** S4, the observable behaviour of `Lib/typing.py` (identity
  functions, introspectable `GenericAlias`-like objects, `TypedDict` being a
  plain `dict` at runtime).

The shim's contracts are therefore mostly identities and constructors —
`cast(t, v)` carries `#@ ensures \result == v`, full stop — and the runtime
plane is deliberately *thin*. Its one structural novelty is reification: where
a type expression flows into a value position (`get_origin`/`get_args`
arguments), the front-end quotes the annotation into a `#@ datatype TypeExpr`
value. That quoting step is the literal link between the parser's type
language and the model.

### 2.3 The no-blending rule and the soundness report

A construct whose two planes disagree carries **both** contracts, separately
labelled, never merged. Canonical example: a `@runtime_checkable Protocol`'s
`isinstance` checks method *presence only* (S3/S4), while static conformance
is full-signature behavioural refinement (S1). Encoding the static meaning into
the runtime check — or letting the weak runtime check stand in for conformance
— is the coherent-and-wrong failure applied to types.

To keep the boundary machine-visible, `--soundness-report` gains a per-
annotation classification alongside Modelled/Specified/Stubbed/Confinement:

- **Interpreted** — the annotation is consumed by the static plane and lowered
  to obligations (a `Literal` that became a `requires`, an `Optional` that
  became a sum type with match obligations).
- **Shimmed** — only its runtime-plane meaning is used (a `cast`, a reified
  introspection value).
- **Ignored** — outside the declared subset; reported, with its GT-gap code,
  never silently dropped.

An annotation the report cannot classify is a defect in the same sense as an
unclassified escape hatch.

### 2.4 Disagreement handling and the conformance gate

Where S1 disagrees with S5 (the conformance suite) or S4 (the runtime), the
disagreement is surfaced as a finding, not resolved by picking the convenient
side — the same instinct as a CPython-doc-vs-behaviour conflict in the stdlib
work. PyCSL declares the subset of S5 it claims, runs that subset as a gate
(the typing analogue of the stdlib differential in §3), and the undeclared
remainder is, by construction, the residual the report's **Ignored** class and
the GT codes account for.

---

## 3. Total control of the AST: `frontend/pure_ast.py`

The static plane is only governable because PyCSL owns its entire parsing
chain. `pure_ast.py` is a pure-Python reimplementation of the stdlib `ast`
module: the complete node hierarchy is generated from an ASDL-derived table
(`_NODE_SPEC`), and `parse` tokenizes with the stdlib's pure-Python `tokenize`
and runs a hand-written recursive-descent parser — **no `compile`, no C
`_ast`**. Two properties of that file are load-bearing for `typing`:

**Loud failure, never a wrong tree.** Unsupported constructs raise
`PyCSLSyntaxError` instead of producing an incorrect tree, and the acceptance
gate is differential: against CPython 3.12's stdlib, 512/517 files parse to a
byte-identical `ast.dump`, 0 mismatches, 0 crashes, with the 5 deferred files
failing loudly. This is exactly the property a *specified annotation
sub-language* needs: a type expression outside the interpreted subset is
rejected at the layer that owns syntax, with a clear error, rather than
mis-modelled downstream.

**The typing schema is already in the node layer; only productions are
deferred.** `_NODE_SPEC` already defines `TypeAlias`, the `type_param` family
(`TypeVar`, `ParamSpec`, `TypeVarTuple`), and the `type_params` field on
`FunctionDef`/`ClassDef`. The COVERAGE MANIFEST lists the PEP 695 surface —
`def f[T]`, `class C[T]`, the `type X = ...` alias statement — and
`type_comments=True` as deliberate loud-fails. Implementing `typing`'s modern
syntax is therefore a **parser-internal change wholly under project control**:
add the `_Parser` productions (and the matching `unparse` arms) against S6,
and extend the differential so the deferred-construct files flip from
loud-fail to byte-identical. The gate inherits the project's gated
byte-identity invariant: every previously-passing file must keep a
byte-identical dump.

Three further consequences of owning the parser:

1. **Static evaluation of string annotations.** Under
   `from __future__ import annotations` (PEP 563) annotations are strings;
   `typing.get_type_hints` evaluates them at runtime. PyCSL instead re-parses
   annotation strings *statically* through `pure_ast.parse` in `eval` mode —
   the same parser, the same loud-fail discipline, and never `eval`. Forward
   references become a front-end resolution problem with a specified order
   (GT5), not a runtime one. (PEP 649's deferred-evaluation runtime, arriving
   in later CPythons, changes S4's mechanism but not this static route.)
2. **One ingestion point for both specification languages.** `comments()`
   harvests `#@` contract comments (Module 1 ingestion) from the same owned
   front-end that parses annotations, so CSL contracts and typing annotations
   can be *coherence-checked against each other* at ingestion — e.g. an
   `Optional[int]` parameter whose contract says `requires x != None` is a
   redundancy to normalize; an `int` parameter with `requires x == None` is a
   contradiction to surface.
3. **The annotation sub-grammar is specifiable.** Because the type-expression
   fragment (names, subscriptions, `|` unions, `Literal[...]` arguments,
   PEP 695 parameter lists) is parsed by productions the project writes, the
   concrete-syntax reference can specify it exactly, with error codes, like
   any `#@` directive — the parser is where "total control" becomes a
   checkable claim rather than a slogan.

---

## 4. Whole-module monomorphization and the tier taxonomy

### 4.1 Why monomorphization

PyCSL proves whole modules in a closed world; that is also exactly the world
in which generics can be discharged by **monomorphization**: collect every
concrete instantiation of a generic in the module (plus resolved imports),
emit one specialized WhyML `let`/`val` per instantiation with types and
contracts substituted, and prove each copy as an ordinary monomorphic
function. WhyML's logic admits prenex polymorphism, but PyCSL's *program*
emission surface — abstract `val` stubs, record-typed module globals, the
int-coercion discipline, the contract-propagation maps — is concretely typed
throughout; monomorphization keeps that entire Module 6 surface unchanged per
instance instead of threading type variables through it. The costs are honest
and acceptable: VC volume scales with the number of instantiations (mitigated
by the same `no_inline`/contract-opacity boundaries used everywhere else), and
polymorphic recursion does not terminate under monomorphization, so it is a
loud-fail (GT4), not a silent approximation.

What monomorphization is NOT: it is not separate compilation (the closed
whole-module world is the enabling assumption, the same one the existing proof
pipeline makes); it is not gradual (`Any` never instantiates a `TypeVar`,
GT1); and an un-instantiated generic gets no program emission at all — only
its declaration is checked, and the report says so.

### 4.2 The tiers (stable taxonomy)

The codes TY0–TY3 are introduced here as stable taxonomy in the manner of the
UB-7.x catalogue. Ordering is by mechanism reuse, and a tier ships only when
the tier below has its reference sections, corpus prove/fail pairs, and
soundness-report classification in place.

| Code | Layer | Constructs | Mechanism (lowering locus) |
|------|-------|-----------|-----------------------------|
| **TY0** | the de facto baseline | scalar annotations (`int`, `str`, `bool`, `bytes`), known class names, container shapes the front-end already reads, `None` returns | none to build — **specify what already exists** (S7 → the three references, with error codes); the precondition for everything else |
| **TY1** | monomorphic refinements | `Optional[X]` / `Union` / `X \| Y` (→ Why3 sum types; `is None`/`isinstance` branches become match path-conditions in WP), `Literal[...]` (→ ground `requires`/invariants, SMT-cheap), `Final`/`ClassVar` (→ write-exclusion obligations, a degenerate HAPPY-style meta-property: no write site outside `__init__`), `NoReturn`/`Never` (→ `\diverges`/false postcondition hooks), `cast`/`NewType`/`assert_type` (shim identity + free static assertion) | Module 6 lowering table + injected obligations; no type variables anywhere |
| **TY2** | monomorphic aggregates & interfaces | `TypedDict`/`NamedTuple` (→ WhyML records; total vs partial `TypedDict` via presence ghosts), `@overload` (→ a guarded contract family — each signature a `requires_i ⟹ ensures_i` — proved against the single implementation; runtime plane: bodies discarded per S3), `Protocol` (→ a **contract interface**: conformance is per-method behavioural refinement, Liskov obligations a deductive verifier discharges natively; `runtime_checkable` stays presence-only per §2.3) | contract-family machinery + record emission; still no type variables |
| **TY3** | the generic layer | `TypeVar`/`Generic[T]` and the PEP 695 forms (`def f[T]`, `class C[T]`, `type X = ...`), bounded type variables, restricted `Callable` | **whole-module monomorphization**: the front-end collects instantiation sites; per concrete instantiation Module 6 emits a name-mangled specialized copy (`Stack_int`) with substituted contracts and proves it; a `TypeVar` bound becomes an instantiation-time obligation (the type argument must supply the bound's operations/contracts); `Callable[[A], B]` is restricted to references to top-level functions with known contracts, defunctionalized per call site; variance is deferred (GT2) |

Two seams worth naming now because they cut across tiers. First, TY1's sum
types are where Python's *narrowing* lands in WP terms: a path condition under
an `is None` test selects a constructor, so narrowing is match lowering, not a
separate analysis — and `TypeIs`/`TypeGuard` functions (PEP 742) are exactly
functions whose boolean result carries a constructor fact, i.e. an
`ensures \result == True ⟹ <shape>` contract, a correspondence PyCSL gets for
free. Second, TY3's parser dependency: the PEP 695 productions of §3 must land
(with the differential flipped) before TY3's front-end work begins; the older
`TypeVar("T")` spelling can be interpreted earlier since it parses today.

### 4.3 Cross-cutting obligations (every tier, no exceptions)

Each construct ships only with: its production in the concrete-syntax
reference (citing S6), its well-formedness rule and error code in the
static-semantics reference (citing S1/S2), its §T lowering section in the
translational reference, an `annotations.md` canonical entry, corpus
prove/fail driver pairs, classification in the extended soundness report
(§2.3), the declared S5 conformance-subset entries it claims, and a clean
`bin/doc-coherency.py --check`. A construct that lowers correctly but whose
Ignored/Interpreted boundary is invisible to the report is not done.

---

## 5. Gap analysis

- **GT1 — `Any` is refused, not interpreted.** Gradual typing's consistency
  relation is intransitive and deliberately unsound; importing it would let a
  value launder through any contract. `Any` in verified code is either
  rejected or treated as an opaque type supporting no operation without
  explicit narrowing, and every occurrence is reported. Permanent, by design.
- **GT2 — Variance is deferred.** Co/contravariance of generic parameters
  (declared or PEP 695-inferred) is not interpreted in TY3's first delivery;
  instantiations are checked invariantly (stricter than S1, per §2.1).
- **GT3 — `ParamSpec` / `TypeVarTuple` are schema-only.** The node layer
  carries them (S6/`_NODE_SPEC`); no static interpretation is planned inside
  TY0–TY3.
- **GT4 — Polymorphic recursion is a loud-fail.** Monomorphization does not
  terminate on it; the front-end rejects with a dedicated error code rather
  than approximating.
- **GT5 — Forward references need a specified resolution order.** Stringized
  annotations referencing not-yet-bound names are resolved statically (§3.1);
  the resolution order and its failure modes must be specified with TY0.
- **GT6 — `# type: ignore` is not honoured.** Honouring it would be an
  unaudited trust hatch; the only sanctioned suppression remains the explicit,
  provenance-carrying `\trusted reviewer:` route.
- **GT7 — Runtime-checkable `Protocol` semantic gap.** `isinstance` presence
  checking vs static full conformance (§2.3) is a permanent two-plane split;
  both meanings are carried separately, neither stands in for the other.
- **GT8 — The S5 conformance subset is not yet declared.** Until the declared
  subset and its gate exist, no public conformance claim is made.
