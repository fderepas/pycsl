# `@overload` (PEP 484) — Two-Plane Spec

**Status:** Two-plane spec for the `@overload` construct. Authored by the typing-spec-agent
under the TY2 tier. This document carries the static claim, the runtime claim, the
divergence between them, and the Interpreted/Shimmed/Ignored classification — in four
sections that must NOT be merged. It cites the S1–S7 authorities per §3.1 of
`typing-global-impl.md` and proposes NO lowering (that is the core-agent's job). Each
static obligation clause is stated so it maps to one VC or one S5 conformance case; each
runtime claim is checked against S3's negative sentence (annotations are not enforced)
resolved by S4.

**Authorities cited in this spec:**
- **S1** — the typing specification (typing.readthedocs.io, Typing Council / PEP 729). The
  overload-resolution rules live under "Function overloading" / "Overloads" in the typing
  spec. Where S1 and PEP 484 (S2) conflict, S1 wins.
- **S2** — PEP 484 (Type Hints, §"Overloads") introduces the `@overload` decorator: a
  sequence of `@overload`-decorated stubs (each with `...` body) declaring the type
  signatures, followed by exactly one non-`@overload` implementation. PEP 612 (S2) and
  PEP 646 (S2) refine parameter-form handling; PyCSL's TY2 scope is the monomorphic
  parameter-type case (TypeVar/ParamSpec are TY3, GT4 loud-fail).
- **S3** — the library reference (`docs.python.org/3/library/typing.html#typing.overload`):
  central sentence is NEGATIVE — the runtime does not enforce annotations; moreover S3
  explicitly says the `@overload`-decorated definitions "are discarded at runtime" and the
  non-overload implementation is what runs. `get_overloads`/`clear_overloads` provide
  introspection only.
- **S4** — CPython `Lib/typing.py` observable behaviour (the runtime lower bound):
  `overload(func)` registers `func` in `_overload_registry` keyed by
  `(module, qualname, firstlineno)` and returns `_overload_dummy`, a function that RAISES
  `NotImplementedError` if called. The `@overload`-decorated name is therefore bound to
  `_overload_dummy` at runtime until the final non-`@overload` `def` rebinds the name to the
  implementation. The stubs survive ONLY in `_overload_registry`, retrievable via
  `get_overloads(func)`. The implementation is a plain function with no overload-specific
  runtime behaviour.
- **S5** — the typing conformance test suite (static executable ground truth).
- **S7** — PyCSL front-end current behaviour (TY0 baseline): `@overload` is currently
  treated as a plain decorator. Each `@overload def f(...)...` stub is emitted as a
  function IR node with an `...` (pass) body; the `@overload` decorator itself is recorded
  but has NO static-plane effect. The final non-overload `def f(...)` is emitted as a
  separate function, overwriting the stub name. There is currently NO overload-family
  recognition and NO guarded-contract synthesis — this is the unspec'd de-facto behaviour.

---

## 1. STATIC PLANE

The static plane treats an `@overload` family as a **guarded contract family**: a set of
N ≥ 1 stubs, each declaring a parameter-type signature and a (possibly empty) postcondition,
collapsed onto ONE implementation. Each stub's postcondition is **guarded** by a predicate
that characterizes its parameter types; at a call site, the argument's static type selects
the stub whose guard it satisfies, and that stub's guarded postcondition applies. The static
meaning is a set of *judgments about programs* — overload-family recognition, guard
synthesis, call-site selection, and the no-blend rule against runtime isinstance dispatch —
each stated below as an obligation clause precise enough to map to one VC or one S5
conformance case. Nothing in this section claims anything happens at runtime; runtime claims
live in §2.

### 1.0 Syntax forms (PEP 484)

- **O1 (the overload family).** A function `f` is an overload family iff there exist N ≥ 1
  `@overload`-decorated stubs `@overload def f(p_i: T_i) -> R_i: ...` (each with a literal
  `...` body) followed by exactly one non-`@overload` implementation
  `def f(p) -> R_impl: <body>`, all at the same scope and same name `f`. — *cites S1, PEP 484
  (S2).* Field order is significant: the stubs' declaration order is the resolution order
  (first match wins).
- **O1a (stub body is `...`).** Each `@overload` stub's body is the literal `...` (Ellipsis)
  or `pass` — it carries NO executable code; it is a pure signature declaration. A stub with
  a non-`...` body is NOT an overload stub (it is a regular decorated function). — *cites S1,
  PEP 484 (S2).*
- **O1b (exactly one implementation).** After the stubs, exactly one `def f(...)` WITHOUT
  `@overload` is the implementation. Zero implementations is a static error (the family is
  unresolved); more than one is a static error. — *cites S1, PEP 484 (S2).*

### 1.1 Guard synthesis

- **O2 (guard per stub, the load-bearing rule).** For each overload stub `i` with parameter
  `p_i: T_i`, the static plane synthesizes a **guard** `G_i` — a predicate over the
  implementation's parameter that is TRUE iff the argument's static type is assignable to
  `T_i`. For the monomorphic TY2 scope, `G_i` is a conjunction of per-parameter
  type-predicate tests derived from `T_i` (e.g. `T_i = int` ⇒ `is_int(p)`; `T_i = str` ⇒
  `is_str(p)`). — *cites S1, PEP 484 (S2).* One S5 case: a value of type `int` selects the
  `int` overload; one S5 case: a value of type `str` selects the `str` overload.
- **O3 (guarded postcondition).** For each stub `i` carrying a postcondition `Q_i(\result)`
  (from a `#@ ensures Q_i` on the stub), the static plane attaches to the implementation
  the **guarded postcondition** `ensures { G_i -> Q_i(\result) }`. A stub with no
  postcondition contributes no guarded clause (its guard is still synthesized for selection
  but it adds no VC). — *cites S1, PEP 484 (S2).* One VC per stub carrying a postcondition.
- **O4 (selection at call sites).** At a call site `f(v)` where `v` has static type `T_v`,
  the active overload is the first stub `i` (in declaration order) whose guard `G_i` is
  satisfied by `T_v`. The selected stub's guarded postcondition `G_i -> Q_i(\result)`
  applies; if `Q_i` is absent, no extra postcondition applies beyond the implementation's
  own. The selection is a **type-based VC**: it is discharged by proving `T_v` assignable
  to `T_i`, NOT by any runtime check. — *cites S1, PEP 484 (S2).* One S5 case: a call with
  an `int` argument proves the `int`-overload's postcondition.

### 1.2 The no-blend rule (static side)

- **O5 (selection is type-based, NOT runtime-dispatch-based).** The static overload-
  selection obligation (O4) is discharged by a **type-based VC** — the argument's static
  type against the stub's parameter type. It must NOT be discharged by the implementation's
  runtime `isinstance` dispatch. A lowering that let `if isinstance(x, int): ...` in the
  implementation SATISFY the static "the int overload's postcondition applies" obligation
  would blend the planes: the runtime isinstance is a value check; the static selection is
  a type judgment. The two are carried as SEPARATE facts. — *cites S1; the no-blend rule
  (§0 of `typing-global-impl.md`).* One S5 case: a call `f(v: int)` selects the int
  overload by type alone, even if the implementation has no isinstance branch.
- **O6 (the implementation proves each guarded postcondition).** The implementation body
  must prove EACH guarded postcondition `G_i -> Q_i(\result)` against its single body. The
  guards partition the input space; for each `i`, under the assumption `G_i`, the body
  must establish `Q_i`. This is a family of VCs over one body — the "guarded contract
  family proved against the single implementation" (TY2 hard rule). — *cites S1, PEP 484
  (S2).* One VC per guarded postcondition.

### 1.3 Expressibility check (dischargeability, NOT a lowering proposal)

Each clause above is stated so that it can be discharged by SOME mechanism the core-agent
may choose: a guarded postcondition `ensures { G_i -> Q_i(\result) }` is a WhyML
implication in an `ensures` clause (Why3 supports implication in postconditions natively —
see `module6_whyml/statements.py:171` et al. for the existing `ensures { ... -> ... }`
emission pattern); the guard `G_i` is a type-predicate over the parameter (the existing
`is_int`/`is_str` predicate vocabulary reused from the Union/Optional narrowing seam);
call-site selection is the argument-type-to-stub-parameter-type assignability VC (native
Why3 type-checking when the stub's parameter type is a ground type like `int`/`str`). The
spec-agent confirms each clause is dischargeable by some such mechanism; the choice of
mechanism is the core-agent's, not this spec's. **The core-agent's hard rule
(`typing-global-impl.md` §5, TY2): overload is a guarded contract family — multiple
`@overload`-decorated stubs (each with different parameter types + a guarded postcondition)
collapsed onto ONE implementation, the guards selecting which overload's postcondition
applies. NO `\trusted`.**

---

## 2. RUNTIME PLANE

The runtime plane says what `@overload` does when the program runs. S3's central sentence
is NEGATIVE: the Python runtime does NOT enforce function and variable type annotations.
S3 is even more pointed for `@overload`: the `@overload`-decorated stubs "are discarded at
runtime" — only the implementation runs. So the runtime meaning of `@overload` is almost
nothing: the decorator registers the stub for introspection and returns a dummy that raises
if called; the implementation is a plain function.

### 2.1 `@overload` stubs are discarded at runtime

- **R1 (stub bodies are discarded).** Each `@overload def f(...): ...` stub has a literal
  `...` body (O1a). At runtime the stub body is never executed: the `@overload` decorator
  returns `_overload_dummy` (S4), which RAISES `NotImplementedError` if called. So calling
  a stub-named function before the implementation is bound raises. — *cites S3
  (`typing.overload` — "discarded at runtime"); resolved by S4 (`_overload_dummy`).*
- **R2 (the implementation runs).** The final non-`@overload` `def f(...)` rebinds the name
  `f` to the implementation function. Calls to `f(...)` after that point invoke the
  implementation, which is a plain Python function with NO overload-specific runtime
  behaviour. Its parameter annotations (if any) are NOT enforced (the central negative
  sentence). — *cites S3; resolved by S4.*
- **R3 (no type enforcement at runtime).** The runtime does NOT check that the argument's
  type matches any overload stub's parameter type. The implementation accepts whatever
  runtime arguments it accepts; wrong-typed arguments flow through unless the
  implementation's own code (e.g. an `isinstance` branch) rejects them — and that is the
  implementation's logic, NOT overload enforcement. — *cites S3 (central negative sentence);
  resolved by S4.*
- **R4 (isinstance dispatch is implementation logic, not overload resolution).** If the
  implementation contains `if isinstance(x, int): return x; return x`, that is ordinary
  runtime control flow — it is NOT the static overload selection. The runtime isinstance
  check operates on VALUES; the static selection operates on TYPES. They are different
  things. (This is the runtime-side restatement of the no-blend rule, O5.) — *cites S3, S4.*

### 2.2 Introspection

- **R5 (get_overloads returns the stubs).** `typing.get_overloads(f)` returns a list of the
  `@overload`-decorated stub function objects registered for `f` (in registration order,
  keyed by firstlineno). This is introspection only — it does not enforce anything.
  `typing.clear_overloads()` empties the registry. — *cites S3 (`get_overloads`);
  resolved by S4 (`_overload_registry`).*

### 2.3 Identity / shim faithfulness

- **R6 (no validation in the shim).** Any `src/pycsl_lib/typing` shim for `overload` must
  agree with S4: the decorator registers the stub and returns a dummy; it performs NO
  type-checking of arguments. A shim that CHECKED whether a call matches an overload's
  parameter types would be unfaithful in exactly the way an over-strong axiom is. — *cites
  S3, S4.*
- **R7 (the implementation is a plain function).** The runtime plane of the implementation
  is just the plain-function plane — there is no separate overload runtime behaviour beyond
  the registry and the dummy. — *cites S3, S4.*

---

## 3. DIVERGENCE

The two planes disagree, and the disagreement is permanent: neither plane's claim may
stand in for the other. Stating them as a single contract is the canonical
coherent-and-wrong failure (typing edition), and for `@overload` the trap is sharpest
because the implementation's `isinstance` dispatch LOOKS like it is doing overload
resolution.

- **D1 (type-based selection vs runtime isinstance dispatch).** The static plane (§1)
  selects the active overload by a **type-based VC**: the argument's static type against the
  stub's parameter type (O4/O5). The runtime plane (§2) may run an `isinstance` branch in
  the implementation (R4), but that is a VALUE check on the runtime value, NOT the type
  judgment. A lowering that let the runtime `isinstance` dispatch SATISFY the static
  overload-selection obligation would blend the planes. The two are carried as SEPARATE
  facts: the static selection VC is discharged by type assignability; the runtime isinstance
  is discharged by the implementation's body executing.
- **D2 (stubs discarded vs stubs-as-contracts).** The static plane treats the stubs as a
  contract family (each stub contributes a guarded postcondition, O3). The runtime plane
  discards the stubs (R1 — `_overload_dummy` raises). The static contract family is NOT
  carried by the runtime stubs; the runtime stubs carry nothing (they raise if called).
- **D3 (implementation proves the family vs implementation is a plain function).** The
  static plane proves EACH guarded postcondition `G_i -> Q_i(\result)` against the single
  implementation body (O6). The runtime plane treats the implementation as a plain function
  with no overload-specific behaviour (R2/R7). The runtime function does not "know" it is an
  overload implementation.
- **D4 (no-blend invariant).** The static plane's obligations (§1) and the runtime plane's
  discard-and-plain-function behaviour (§2) are carried as SEPARATE contracts, separately
  labelled. An `@overload` family whose runtime isinstance dispatch passes the static
  overload-selection VC is a finding (gap doc), not a success — because the static VC must
  be discharged by type assignability, independent of the runtime isinstance. The no-blend
  rule is defended by author separation: this spec-agent and the conformance-agent never
  read the core-agent's lowering.

---

## 4. CLASSIFICATION

- **Static plane: INTERPRETED.** An `@overload` family is consumed by the static plane and
  lowered to a guarded contract family attached to the single implementation: each stub
  contributes `ensures { G_i -> Q_i(\result) }` (O3); the implementation proves each guarded
  postcondition (O6); call sites select the active overload by type-based assignability
  (O4). Each clause O2–O6 maps to one VC or one S5 conformance case. The construct is
  classified **Interpreted** in `--soundness-report`.
- **Runtime plane: SHIMMED.** The runtime meaning of `@overload` is the discard-and-plain-
  function behaviour (stubs return `_overload_dummy` which raises; the implementation is a
  plain function; `get_overloads` returns the registered stubs) plus the introspectable
  registry. Any `src/pycsl_lib/typing` surface for `overload` is a thin shim that registers
  the stub and returns a dummy, performing no validation. The construct is classified
  **Shimmed** in `--soundness-report`.
- **Combined classification:** `@overload` is **Interpreted on the static plane, Shimmed
  on the runtime plane** — both classifications apply, separately, per the no-blend rule
  (§3 of `typing-global-overview.md`).

### GT gap codes tagged in this spec

- **GT7** (analogous, NOT a new code) — D1 documents the `isinstance`-dispatch no-blend
  trap: the static O4/O5 type-based-selection obligation must NOT be discharged by any
  runtime `isinstance` check in the implementation (R4 is value dispatch, not type
  judgment). This is the overload-local restatement of the no-blend rule, tagged in the
  report as a `no_blend_overload_isinstance` note, not a new GT code.
- **GT8** — S5 conformance subset. The S5 subset for `@overload` is not yet declared; it
  is the conformance-agent's standing artifact. Each clause O2–O6 above names the S5 case
  shape it commits to; the declared subset is built from those case shapes.

No other GT gap is tagged in this spec. GT1 (`Any`), GT2 (variance), GT3
(`ParamSpec`/`TypeVarTuple`), GT4 (polymorphic recursion), GT5 (forward-reference
resolution order, owned by TY0), and GT6 (`# type: ignore`) are out of scope for
`@overload` at TY2. TypeVar-bearing overloads are TY3 (the monomorphic TY2 scope uses only
ground parameter types like `int`/`str`).
