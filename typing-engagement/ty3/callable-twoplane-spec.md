# `Callable` (PEP 484) + PEP 695 type-parameter surface — Two-Plane Spec

**Status:** Two-plane spec for the FINAL TY3 construct: `Callable[[ArgTypes], Ret]`
(PEP 484) and the PEP 695 type-parameter surface confirmation. Authored by the
typing-spec-agent under the TY3 tier per `typing-global-impl.md` §2/§5. This
document carries the static claim, the runtime claim, the divergence between
them, and the Interpreted/Shimmed/Ignored classification — in four sections that
must NOT be merged. It cites the S1–S7 authorities per §3.1 and proposes NO
lowering (that is the core-agent's job). Each static obligation clause is stated
so it maps to one VC or one S5 conformance case; each runtime claim is checked
against S3's negative sentence (annotations are not enforced) resolved by S4.

This construct has TWO related surfaces, both already partly landed:
1. **`Callable` (PEP 484).** `Callable[[int, str], bool]` is a *function type*.
   The static plane synthesizes a function-type obligation on the parameter; the
   runtime plane is an introspectable alias object with NO enforcement.
2. **PEP 695 type-parameter surface.** The parser (commit 8335eede) and the
   monomorphization machinery (commit 89f3acec) ALREADY landed and graduated
   (TypeVar/Generic two-plane spec, Gate C PASS). This spec CONFIRMS the PEP 695
   surface flows end-to-end through the monomorphizer (the `type_params` IR
   field) and is documented as a first-class surface — no new lowering is
   proposed for it here; it is a confirmation + first-class-documentation
   surface only.

**Authorities cited in this spec:**
- **S1** — the typing specification (typing.readthedocs.io, Typing Council /
  PEP 729). The "Callable" and "Generics" / PEP 695 "Type parameter syntax"
  sections are authoritative. Where S1 and PEP 484/695 (S2) conflict, S1 wins.
- **S2** — PEP 484 (`Callable`), PEP 695 (`def f[T]`, `class C[T]`). Rationale
  and fine print; yields to S1 on conflict.
- **S3** — the library reference (`typing.html#typing.Callable`). The central
  sentence is NEGATIVE: the runtime does not enforce annotations. A
  `Callable[...]` subscript constructs an introspectable *alias object*; it does
  NOT specialize code, does NOT check that a value conforms to the signature at
  runtime, and `isinstance(x, Callable)` is a presence check only (callable()).
- **S4** — CPython `Lib/typing.py` observable behaviour (the runtime lower
  bound the shim must be faithful to). `Callable[[int, str], bool]` constructs a
  `CallableAlias` / `_CallableGenericAlias` object recording `__args__ = (int,
  str, bool)` for introspection; it does NOT run at a call site. `callable(x)`
  is the builtin (not `typing`), returning `True` iff `x` has a `__call__`
  attribute — a PRESENCE check, signature-agnostic.
- **S5** — the typing conformance test suite (static executable ground truth).
  PyCSL declares the subset it conforms to (§1.5); the declared subset covers
  the function-type obligation at a call site (arg-type match + result type).
- **S6** — the CPython 3.12 grammar / ASDL. `Callable[...]` is a `Subscript`
  (PEP 484); PEP 695 `type_params` is on `ClassDef`/`FunctionDef` (landed in
  `pure_ast.py`, commit 8335eede). Cited by the parser productions (S6).
- **S7** — PyCSL front-end current behaviour (TY0 baseline). The front-end
  PARSES `Callable[[int], int]` as a `Subscript` annotation but the IR emitter
  DROPS the arg/return types — the parameter is recorded with the bare tag
  `"callable"` which lowers to the WhyML `int` fallthrough. A call site `f(n)`
  on such a parameter already lowers to WhyML application `(f n)`, but the
  parameter is typed `int` so Why3 rejects it ("int cannot be applied"). This is
  the unspec'd de-facto behaviour TY0 pins and this construct replaces: the
  parameter must lower to a WhyML *function type* `int -> int` so the existing
  application type-checks soundly.

---

## 1. STATIC PLANE

The static plane treats a `Callable[[A1, ..., An], R]`-typed parameter as a
**function-type obligation**: the parameter is a value of function type
`τ(A1) -> ... -> τ(An) -> τ(R)`. The proof obligation arises at each CALL SITE
on that parameter: the argument types must match the Callable's arg-type list
and the call yields a value of type `τ(R)`. This is discharged by Why3's own
type system at the application site (the existing application lowering). Nothing
in this section claims anything happens at runtime; runtime claims live in §2.

### 1.0 Syntax form (PEP 484)

- **C0 (Callable annotation).** `f: Callable[[A1, ..., An], R]` declares that
  `f` is a function accepting arguments of types `A1..An` (in order) and
  returning a value of type `R`. The `Callable[...]` subscript appears as a
  parameter/return/local annotation. The arg-list is a literal Python list
  `[A1, ..., An]`; `R` is the return type. `Callable[..., R]` (ellipsis) and
  `Callable[[A1, ...], R]` (concatenation, `ParamSpec`-derived) are NOT
  interpreted in this delivery (GT3 — `ParamSpec` is schema-only). — *cites S1,
  PEP 484 (S2).*

### 1.1 Function-type obligation on the parameter

- **C1 (parameter lowers to a function type).** A parameter `f` annotated
  `Callable[[A1, ..., An], R]` lowers to a WhyML parameter of function type
  `τ(A1) -> ... -> τ(An) -> τ(R)` (a curried Why3 arrow type). The function-type
  is the *contract*: it obliges any caller of the enclosing function to supply a
  function value of that exact signature. — *cites S1; the "reuse the existing
  function-contract machinery" directive (Why3 function types + application).*
  - *S5 mapping:* one case — `def g(f: Callable[[int], int], n: int) -> int:
    return f(n)` type-checks (the application `f n` is well-typed, result `int`).

### 1.2 Call-site arg-type obligation

- **C2 (call-site arg-type match).** At a call site `f(a1, ..., an)` on a
  `Callable[[A1, ..., An], R]`-typed `f`, the argument types must match the
  Callable's arg-type list positionally; the call yields a value of type `R`.
  This is discharged by Why3's application typecheck (the existing `(f a1 ... an)`
  lowering). A type mismatch is a static REJECT (a WhyML type error). — *cites S1,
  PEP 484 (S2).*
  - *S5 mapping:* one pass case — `f(n)` with `f: Callable[[int], int]`, `n: int`
    type-checks; one reject case — `f(s)` with `s: str` is a WhyML type error
    (str vs int).

### 1.3 Result-type obligation

- **C3 (result type is R).** The result of a call on a `Callable[[...], R]`-typed
  value has type `τ(R)`. A function whose body is `return f(...)` therefore has
  return type `τ(R)`. A declared return annotation that disagrees with `τ(R)` is
  a static REJECT (WhyML type error). — *cites S1, PEP 484 (S2).*
  - *S5 mapping:* one reject case — `def g(f: Callable[[int], int]) -> str:
    return f(0)` is a WhyML type error (int vs str).

### 1.4 No value postcondition from a bare Callable

- **C4 (a bare Callable gives NO value postcondition).** A parameter typed
  `Callable[[A], R]` guarantees only the arg/result TYPES; it does NOT guarantee
  any specific return VALUE. A postcondition on the enclosing function that
  asserts a specific value of `f(...)` (e.g. `ensures \result == x + 1` where the
  body is `return f(x)`) is UNPROVABLE — `f` is an opaque function value. This is
  *sound*: the static plane refuses to claim a value theorem the function-type
  does not justify. A strengthening requires a `#@ conforms_to`-style contract on
  the callable value (out of scope for this delivery; future work). — *cites S1;
  the no-blend rule (§3).*
  - *S5 mapping:* one reject case — `def g(f: Callable[[int], int], x: int) ->
    int: #@ ensures \result == x + 1; return f(x)` is UNPROVABLE (correct sound
    refusal — NOT a `\trusted` shortcut).

### 1.5 Scope limit (stricter than S1, sound)

- **C5 (primitive arg/return types only).** This delivery supports `Callable`
  arg/return types that are PyCSL primitive tags (`int`, `bool`, `str`, `bytes`,
  `float`) and record-typed names. A nested `Callable` inside a `Callable` arg
  list, a `ParamSpec`-derived `Callable[...]`, or an `Any` arg/return is NOT
  interpreted (refused with a located error). This is *stricter than S1* (which
  admits arbitrary arg/return types) and is legitimate divergence-by-strictness.
  — *cites the "may be stricter than S1, never weaker" rule (§0).*

### 1.6 PEP 695 type-parameter surface — CONFIRMATION (no new lowering)

- **C6 (PEP 695 surface flows end-to-end — confirmation).** The PEP 695
  `type_params` field on `ClassDef`/`FunctionDef` (parsed by `pure_ast.py`,
  commit 8335eede) is emitted on the IR (type_decls + functions, IR v1.4) and
  flows through the monomorphizer (`frontend/monomorphize.py:apply_monomorphization`,
  commit 89f3acec) — the COLLECT/EMIT pass consumes `type_params` to specialize
  generics. This spec CONFIRMS the surface is first-class end-to-end: a
  `class C[T]` / `def f[T]` declaration is parsed, IR-tracked, and (when
  instantiated) monomorphized. The PEP 695 surface was already graduated by the
  TypeVar/Generic two-plane spec (Gate C PASS, `conformance/GATE-C-RESULTS.md`);
  this construct records the confirmation and documents the PEP 695 surface as a
  first-class surface alongside `Callable`. No new lowering is proposed for PEP
  695 here. — *cites S1, PEP 695 (S2); the TypeVar/Generic two-plane spec.*

### 1.7 Declared S5 conformance subset

PyCSL declares the following S5 subset for the Callable construct (the static
gate, §Gate C):
- one pass case — `Callable[[int], int]` parameter, call type-checks, result
  `int` (C1/C2/C3);
- one arg-type reject case — `f(s)` with `s: str` on a `Callable[[int], int]`
  param (C2);
- one result-type reject case — `-> str` body `return f(0)` on a
  `Callable[[int], int]` param (C3);
- one unprovability case — a value postcondition on a bare callable is
  correctly UNPROVABLE (C4, the no-blend keystone);
- one PEP 695 confirmation case — `class C[T]` parses + IR-tracks
  `type_params` + monomorphizes on `C[int]()` (C6).
A static claim with no corresponding S5 case is under-specified — gap doc.

---

## 2. RUNTIME PLANE

The runtime plane is *almost nothing*, by S3's central negative sentence: the
runtime does not enforce annotations. A `Callable[...]` at runtime is an
**introspectable alias object**, not a check, not a specialization.

- **R1 (`Callable[...]` constructs an alias object).** `Callable[[int, str],
  bool]` constructs a `CallableAlias`/`_CallableGenericAlias` object recording
  `__args__ = (int, str, bool)` for introspection. No code is specialized; no
  signature check runs at a call site. — *cites S3, S4
  (`Lib/typing.py:_CallableGenericAlias`).*
- **R2 (`callable(x)` is a PRESENCE check).** The builtin `callable(x)` (not
  `typing`) returns `True` iff `x` has a `__call__` attribute — it checks
  callability PRESENCE, NOT signature, NOT arg/return types. `isinstance(x,
  Callable)` (under `runtime_checkable`-style aliasing) likewise checks presence
  only. — *cites S3, S4 (the `callable` builtin).*
- **R3 (NO signature enforcement at runtime).** A function `def g(f:
  Callable[[int], int])` accepts ANY callable at runtime — `g(lambda x: "wrong")
  ` runs without error; the arg/return type mismatch is NOT detected. A shim
  that CHECKED the signature at runtime would be unfaithful to S3's negative
  sentence. — *cites S3, S4.*

The shim's contracts are therefore: `Callable` is an introspectable alias
object (identity, no check); the builtin `callable(x)` is a presence check only.
No runtime-plane contract may assert a function-type obligation (§3).

---

## 3. DIVERGENCE (the no-blend trap, Callable keystone)

The two planes disagree, and the disagreement is the load-bearing soundness
argument for this construct. The canonical Callable trap:

> **The static "this value is a function with signature S" is a proof-time
> judgment; the runtime `callable()` / `isinstance(x, Callable)` is a presence
> check. The static signature obligation must NOT be discharged by the runtime
> callable check.**

- **D1 (static function-type obligation vs runtime presence check).** The static
  plane produces a *function-type obligation* — `f: int -> int` is a WhyML arrow
  parameter, and a call `f(s)` with `s: str` is a static type error. The runtime
  plane produces a *presence check* — `callable(f)` returns `True` for any object
  with `__call__`, signature-agnostic. These are DIFFERENT things on DIFFERENT
  planes. Letting the runtime presence check stand in for the static signature
  obligation — or encoding the static signature into the runtime check — is the
  coherent-and-wrong failure, typing edition.
- **D2 (no value theorem from a bare callable — C4).** The static plane refuses
  to claim a value theorem (`\result == x + 1`) for a bare `Callable` parameter;
  the runtime plane has nothing to say about values. The divergence is that the
  static plane is *stricter than the runtime* (the runtime would happily run any
  callable). A `\trusted` shortcut that asserted the value theorem would blend
  the planes — refused.
- **D3 (PEP 695 surface — no divergence, confirmation only).** The PEP 695
  `type_params` surface carries no new two-plane divergence beyond the
  TypeVar/Generic divergence already recorded (D1–D5 of the TypeVar/Generic
  two-plane spec). This spec confirms the surface flows end-to-end; its
  divergence is the TypeVar/Generic divergence, not a new one.
- **D4 (no-blend invariant, defended by independence).** The rule that the
  planes do not blend has NO external authority — it is defended by the
  independence of the spec-agent and conformance-agent from the core-agent (the
  overview's §4.2 argument). A lowering that quietly let the runtime
  `callable()` check satisfy the static function-type obligation has no way to
  also fool a conformance subset authored from the static spec by someone who
  never saw the lowering. The Gate C (c) check is this guard.

---

## 4. CLASSIFICATION (Interpreted / Shimmed / Ignored)

Per `--soundness-report` extended taxonomy (overview §2.3):

- **Interpreted (static plane lowers to obligations):**
  - `f: Callable[[A1, ..., An], R]` parameter annotation → WhyML function-type
    parameter (C1).
  - Call site `f(a1, ..., an)` on a Callable-typed parameter → WhyML application,
    arg-type + result-type obligations discharged by Why3's typecheck (C2/C3).
  - PEP 695 `type_params` declaration + instantiation → monomorphization
    (C6, inherited from the TypeVar/Generic classification).
- **Shimmed (runtime-plane meaning only):**
  - `Callable[[...], R]` subscript → introspectable alias object (R1).
  - `callable(x)` builtin → presence check (R2). (The builtin is not part of the
    `typing` shim; it is referenced for the divergence statement.)
- **Ignored (outside the declared subset; reported with GT code):**
  - `Callable[..., R]` (ellipsis) / `ParamSpec`-derived `Callable` (GT3 —
    schema-only, loud-fail).
  - Nested `Callable` inside a `Callable` arg list (C5 — stricter than S1,
    refused).
  - `Any` as a Callable arg/return type (GT1 — refused).
  - A value postcondition on a bare callable (C4 — unprovable, NOT shortcut).

### GT ledger (Callable rows; TY3-generic rows inherited from the TypeVar/Generic spec)

| GT | Disposition for Callable | Acceptance line |
|---|---|---|
| GT1 `Any` | refused as a Callable arg/return type | §4 Ignored; `Callable[[Any], int]` rejected |
| GT3 `ParamSpec` | `Callable[..., R]` / `ParamSpec`-derived — schema-only loud-fail | §4 Ignored |
| GT8 declared S5 subset | the conformance gate | §1.7 |

---

## 5. NO LOWERING PROPOSED

This spec proposes no syntax, no IR fields, and no Module 6 emission. It states
the judgments; the core-agent (§2 of the impl guide) designs the Callable
annotation recognition (Module 5), the function-type parameter emission
(Module 6 `_param_type_str`), and the PEP 695 surface confirmation, squeezed by
sound expressibility (may be stricter than S1, never weaker) and total
additivity. A claim this spec cannot state without blending the planes (D1/D2)
is a finding, not something to merge.
