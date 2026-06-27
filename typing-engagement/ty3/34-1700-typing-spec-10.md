# 34-1700-typing-spec-10 — TY3 Callable (PEP 484) + PEP 695 surface confirmation (DONE)

**Status:** DONE (Gate A APPROVED → core-agent implemented → Gate B green →
Gate C green; no gap docs — C4's unprovability is the sound no-blend refusal,
C5 is recorded divergence-by-strictness).
**Construct:** `Callable[[ArgTypes], Ret]` (PEP 484) — the final TY3 construct —
plus a confirmation that the PEP 695 type-parameter surface flows end-to-end.
This is the FINAL construct of the typing engagement; its graduation completes
the entire `typing-global-impl.md` engagement (TY0–TY3).
**Two-plane spec:** `typing-engagement/ty3/callable-twoplane-spec.md` (Gate A APPROVED).
**Probe:** the S7 baseline (a `Callable`-typed param currently lowers to
`(f: int)` and the call site `f(n)` already lowers to WhyML application `(f n)`,
so Why3 rejects "int cannot be applied") — confirming the call-site machinery
already exists; only the parameter TYPE is wrong.

## 1. Design

The lowering is minimal and additive: a `Callable[[A1, ..., An], R]`-typed
parameter lowers to a WhyML **function-type parameter** `τ(A1) -> ... -> τ(An) ->
τ(R)`. The call site `f(a1, ..., an)` already lowers to WhyML application
`(f a1 ... an)` (the existing machinery — unchanged); once `f` carries a
function type, Why3's own typecheck discharges the arg-type match (C2) and the
result type (C3). No `\trusted`. No new IR field.

### 1.1 Where the callable type lives

A `Callable[...]` parameter annotation is recognized in Module 5's
`_m5_get_type_name_legacy` (the Subscript resolver). When `head == "Callable"`,
the arg-list `[A1, ..., An]` and the return type `R` are walked to PyCSL
primitive tags and encoded into the **existing `symbol_table` value string** as
`"callable:<a1>,<a2>,...-><r>"` (e.g. `"callable:int,str->bool"`). This is NOT a
new IR field — the `symbol_table` already carries free-form type-tag strings
(`"Any"`, `"int"`, class names); `"callable:..."` is a new tag VALUE, not a new
field. **No IR_VERSION bump** (IR stays at 1.4). Byte-identical for every
non-Callable driver (the branch triggers only on `head == "Callable"`).

### 1.2 Module 6 — function-type parameter emission

`module6_whyml/functions.py:_param_type_str` gains one branch: if `symtype`
(the symbol_table value) starts with `"callable:"`, parse the encoding and emit
`(f: <whyml-a1> -> <whyml-a2> -> ... -> <whyml-r>)` (a curried Why3 arrow type).
The tag→WhyML map: `int`/`bool`→`int` (PyCSL int-encodes bool), `str`→`string`,
`float`→`real`, a record/variant name→its WhyML name. The call-site application
`(f a1 ... an)` is ALREADY emitted by the existing Call lowering — unchanged.

### 1.3 Scope limit (C5, stricter than S1, sound)

Module 5 refuses (loud-fail `PYCSL-TY3-CALLABLE-SCOPE`) a `Callable` whose
arg/return type is not one of {`int`, `bool`, `str`, `float`, a record/variant
name}. Refused: `bytes` (modeled as a two-param `(loc, len)` — not a single
arrow type), `list`/`dict`/`set`, `Any` (GT1), a nested `Callable`, and
`Callable[..., R]` (ellipsis / `ParamSpec`-derived, GT3). Sound divergence-by-
strictness.

### 1.4 PEP 695 surface confirmation (C6, no new lowering)

The PEP 695 `type_params` field (parsed by `pure_ast.py`, commit 8335eede;
emitted on IR v1.4 type_decls/functions; consumed by `monomorphize.py`,
commit 89f3acec) is confirmed end-to-end by a confirmation driver
(`C6_pep695_surface.py`): a `class C[T]` declaration parses, IR-tracks
`type_params`, and monomorphizes on `C[int]()`. Already graduated (TypeVar/
Generic Gate C PASS); this construct records the confirmation and documents the
PEP 695 surface as first-class alongside `Callable`. No code change for PEP 695.

### 1.5 What is NOT done (deferred / out of scope)

- A contract-strengthening mechanism for callable values (a `#@ conforms_to`-
  style target naming a function-typed contract) — future work (C4 leaves value
  postconditions on bare callables correctly unprovable).
- `bytes`/`list`/`dict`/`set` as Callable arg/return types (C5).
- `ParamSpec`-derived `Callable[Concatenate[...], R]` (GT3, schema-only).
- The `Callable` + generic interaction (`Callable[[T], int]` on a generic
  function — the monomorphizer's string-compare substitution does not rewrite
  inside the `"callable:..."` encoding; out of scope, documented).

## 2. Files to change

| File | Change |
|---|---|
| `src/pycsl/frontend/Module5_IREmitter.py` | `_m5_get_type_name_legacy`: add a `Callable` branch that encodes the arg/return types into `"callable:...->..."`; refuse unsupported types (`PYCSL-TY3-CALLABLE-SCOPE`). Additive — triggers only on `head == "Callable"`. |
| `src/pycsl/module6_whyml/functions.py` | `_param_type_str`: add a `"callable:"` branch emitting a curried Why3 arrow type. Additive. |
| `src/pycsl/core_ir_semantic.py` | Validate the `"callable:"` encoding is well-formed (additive belt-and-suspenders check; a malformed encoding is a static reject). |
| `src/pycsl_lib/typ/__init__.py` | `Callable` runtime shim: a subscriptable introspectable alias object (R1), NO enforcement (R3). |
| `docs/pycsl-concrete-syntax-reference.md` | §T.TY3.5: `Callable[...]` syntax (cites S6/PEP 484). |
| `docs/pycsl-static-semantics-reference.md` | §S.TY3.8: Callable function-type obligation + call-site arg/result obligations (cites S1). |
| `docs/pycsl-translational-reference.md` | §T.TY3.5: Callable → WhyML arrow parameter; call-site application (cites the two-plane spec). |
| `test-suite/annotations.md` | §12.17: canonical `Callable` entry. |
| `typing-engagement/ty3/conformance_callable/` | NEW — S5 subset + S4 shim + no-blend drivers (conformance-agent). |

**No IR_VERSION bump** (no new IR field; the callable descriptor is a new
`symbol_table` tag value). Byte-identical for every non-Callable driver.

## 3. Gates

- **Gate B:** `os` SUCCESS, `formal_os_pure` SUCCESS, `bin/doc-coherency.py
  --check` green, byte-identical emission for every non-Callable driver (the
  Callable branch triggers only on `head == "Callable"` — no corpus driver uses
  it today → 292/292 .mlw byte-identical).
- **Gate C (conformance-agent):** S5 subset (§1.7 of the two-plane spec) + S4
  shim driver; the no-blend trap (D1) — the runtime `callable()` presence check
  must NOT discharge the static function-type obligation.

## 4. IR shape

No change (IR v1.4). The callable descriptor lives in the existing
`symbol_table` value slot as a new tag string `"callable:<args>-><ret>"`. The
field is absent (as before) on every non-Callable function.
