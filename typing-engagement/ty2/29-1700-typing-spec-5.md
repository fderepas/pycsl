# 29-1700-typing-spec-5.md — `TypedDict` Implementation Spec (DRAFT)

**Status:** DONE (core-agent implemented both planes; Gates A/B/C PASS; GAP-001
resolved in the reconcile loop; graduated to Normative).
**Tier:** TY2 (aggregates and interfaces).
**Construct:** `TypedDict` (PEP 589 + PEP 655 `Required`/`NotRequired`).
**Two-plane spec authority:** `typing-engagement/ty2/typeddict-twoplane-spec.md` (Gate A APPROVED).
**Global guides honoured:** `typing-global-impl.md` §0 (no-blend), §4 (per-construct pipeline + gates),
§5 (TY2: "TypedDict/NamedTuple -> WhyML records"). The core-agent hard rule: a TypedDict
class synthesizes a WhyML record `type td = { x: int; y: int }`; field access `p["x"]`
becomes record-field access `p.x`; construction `{"x": 1, "y": 2}` becomes a record literal.
NO `\trusted`.

**This is a planning document. No `src/pycsl/` file is modified by this DRAFT.** On
coordinator APPROVAL, the core-agent implements both planes and runs the standing gate.

---

## 0. Design summary (one paragraph)

`class Point(TypedDict): x: int; y: int` is recognized at the `visit_ClassDef` seam
(`Module5_IREmitter.py:1579`) by checking whether `TypedDict` appears in `node.bases`. For
such classes, a new helper `_collect_typeddict_fields(node)` walks the class body's
AnnAssigns (the field declarations) and synthesizes a `type_decl` of kind `record` whose
`fields` carry the declared per-key types (resolved via the existing
`_field_type_from_annotation` resolver, including the Union/Optional/Final/Literal
normalizers). The record carries NO `__init__`, NO class invariants, NO `bases` — it is a
pure data record. Field access `p["x"]` is recognized at the `_handle_subscript` seam
(`module6_whyml/expressions.py:2151`): when the subscript's receiver is a variable (or
field) whose static type is a known TypedDict record AND the index is a string literal
matching a declared field, the subscript lowers to a record-field read `p.x` via the
existing `_field_label` mechanism. Construction `{"x": 1, "y": 2}` (a dict literal) flowing
into a TypedDict-typed target is recognized at the dict-literal emission seam and lowers to
a record literal `{ x = 1; y = 2 }`. The runtime plane is a thin shim in
`src/pycsl_lib/typ/__init__.py` exposing `TypedDict` as a callable that returns an opaque
introspectable class object (the plain-dict alias) and performs NO validation (R1–R8, D4
no-blend). NO new IR node, NO IR_VERSION bump (reuses the existing `type_decl` (record) and
`Subscript` IR nodes), NO `\trusted`.

---

## 1. Normalization rule (front-end: `src/pycsl/frontend/`)

### 1.1 Surface forms to recognize

Per the two-plane spec §1.0 (T1, T1a, T1b, T1c):

| Surface | AST shape (post-`pure_ast`) | Disposition |
|---|---|---|
| `class Point(TypedDict): x: int; y: int` | `ClassDef(name="Point", bases=[Name("TypedDict")], body=[AnnAssign(...), ...])` | synthesize record `point` with fields `x: int, y: int` |
| `class Point(TypedDict, total=False): ...` | `ClassDef(bases=[Name("TypedDict"), keyword(arg="total", value=Constant(False))])` | synthesize record with `Optional[T]` fields (T1b) |
| `Required[T]` / `NotRequired[T]` field annotation | `Subscript(value=Name("Required"\|"NotRequired"), slice=T)` | per-key totality (T1c); `Required[T]` → `T`, `NotRequired[T]` → `Optional[T]` |
| `Point = TypedDict("Point", {...})` functional form | `Assign(targets=[Name], value=Call(func=Name("TypedDict"), args=[Constant, Dict]))` | TY2-scope: the class form is the priority; functional form is RECOGNIZED but field-extraction is limited to literal `{"name": type}` dicts. If non-literal, no record is synthesized (byte-identical fallback). |

`TypedDict` is recognized by the bare head name in `bases` (the import-rewriting in
`import_classifier.py` already canonicalizes `from typing import TypedDict`).

### 1.2 Canonical IR form

The canonical IR form is a `type_decl` of kind `record`:

```
{ "kind": "record",
  "name": <ClassName>,             # e.g. "Point"
  "fields": [ {"name": "x", "type": "int", "mutable": True}, ... ],
  "class_invariants": [],
  "field_defaults": {"x": 0, "y": 0},   # int-typed fields default 0; string-typed default 0 (the existing int-coded convention)
  "has_hash": False, "has_eq": False, "is_unhashable": False,
  "constants": {}, "bases": [],            # NO base recorded — the record is a pure data type
  "init_params": [], "init_body": [],      # NO __init__ — construction is via dict literal
  "init_ensures": [],
  "is_mixin": False, "compose_from": [],
  "is_typeddict": True                      # NEW optional field (see §5.3 on IR shape)
}
```

The `is_typeddict: True` flag is the ONLY new piece of IR state. It is optional
(`type_decl.get("is_typeddict", False)` reads as `False` for every pre-existing record),
so the IR schema is backward-compatible — no IR_VERSION bump is required. The flag is
consumed by Module 6's `_handle_subscript` and the dict-literal emitter to gate the
TypedDict-specific lowering paths, and by `core_ir_semantic` for the no-blend check (§3).

### 1.3 Normalization steps (in order)

1. **Recognition** — in `visit_ClassDef` (`Module5_IREmitter.py:1579`), BEFORE the existing
   `fields, field_defaults = self._collect_class_fields(node)` call, check
   `_is_typeddict_class(node)`: True iff any `base` in `node.bases` is a `Name` with
   `id == "TypedDict"` OR an `Attribute` with `attr == "TypedDict"`. If True, dispatch to
   `_collect_typeddict_fields(node)` instead of `_collect_class_fields`, and skip the
   `__init__`/mixin/inheritance paths entirely.
   *Byte-identical for non-TypedDict drivers:* the check is a pure base-name test; every
   non-TypedDict class skips it unchanged.

2. **Field extraction** — `_collect_typeddict_fields(node)` walks `node.body` for
   `AnnAssign` whose target is a `Name` (the `x: int` declaration form). For each:
   - resolve the field type via `_field_type_from_annotation(annotation, class_name)`
     (the existing resolver at `:1327`, which already handles `int`/`str`/`bool`/`bytes`/
     `float`/`list`/`dict`/Union/Optional/Final/Literal);
   - apply T1b (total=False) and T1c (Required/NotRequired): if the class is `total=False`
     and the field annotation is NOT `Required[T]`, wrap as `Optional[T]` (synthesizes a
     `_union_<scope>_<idx>` variant with a `None` arm via the existing
     `_normalize_union_annotation` helper). If the annotation IS `Required[T]` /
     `NotRequired[T]`, unwrap and apply the per-key totality.
   - Append `{"name": field_name, "type": resolved_tag, "mutable": True}` to `fields`.
     `field_defaults[field_name]` = `0` (the existing int-coded convention for opaque /
     string-typed / record-typed fields; sound because the field is set at construction
     time, never read before write — the record literal provides every field).

3. **Synthesis** — append the `type_decl` (record) to `program_ir["type_decls"]` with
   `is_typeddict: True`. Populate `program_ir["constructors"]` for the class name so
   `Point(...)` (functional construction) reuses the existing Tier-A parametrized record
   construction (`_call_record_constructor`) — though the primary construction path is the
   dict literal (§2.2).

4. **Functional form** — `_collect_typeddict_functional(node)` walks the module body for
   `Assign` whose value is `Call(func=Name("TypedDict"), args=[Constant(name), Dict(literal)])`.
   If the dict's keys are all string constants and the values are all type expressions, it
   synthesizes the same record `type_decl`. If the dict is non-literal, no record is
   synthesized (byte-identical fallback — the assignment stays an opaque int).

### 1.4 Front-end files that change (on APPROVAL)

| File | Change |
|---|---|
| `src/pycsl/frontend/Module5_IREmitter.py` | add `_is_typeddict_class`, `_collect_typeddict_fields`, `_collect_typeddict_functional`; dispatch from `visit_ClassDef` (`:1579`) and `visit_Module` (where `_synthesize_namedtuple_records` is called). The existing `_collect_class_fields` is NOT modified (byte-identical for non-TypedDict). |

---

## 2. Lowering table entry (Module 6: `src/pycsl/module6_whyml/`)

### 2.1 The lowering

The TypedDict record type_decl lowers through the EXISTING record-emission path in
`module6_whyml/preamble.py` (`:2830`), which already emits `type point = { x: int; y: int }`
for records. The `is_typeddict` flag does NOT change emission — it only gates the
subscript and construction paths below.

### 2.2 Per-clause VC mapping (the load-bearing part)

| Clause | Static obligation | VC / mechanism |
|---|---|---|
| **T2** (record-shape assignability) | `v: Point` assignable to `Point` | Why3 record-type equality (the parameter is typed `point`); a structurally-compatible TypedDict is a separate record type — PyCSL emits a per-field projection+injection goal modeled on the Union per-arm VC. **TY2 scope: same-named assignability only** (a `Point` value flowing into a `Point` parameter); cross-TypedDict structural subtyping is a future TY2 enhancement, flagged as GT-T2-future. |
| **T3** (plain dict NOT assignable) | plain `dict` not assignable to `Point` | Why3 type-checking: a `dict`-typed value has no record type; the parameter's record type rejects it. No new VC — native Why3 type error. |
| **T5** (typed key access) | `p["x"]` has type `int` for `p: Point` | The subscript `_handle_subscript` recognizes a string-literal index into a TypedDict-record-typed receiver and emits `p.x` (a record-field read); Why3 type-checks the field's declared type. An unknown key (`p["z"]`) is a `core_ir_semantic` static error (the field doesn't exist). A non-literal key is a `core_ir_semantic` static error (T5 requires literal keys). |
| **T6** (required-key presence) | `p["x"]` on a total=True TypedDict yields `int` (not `Optional[int]`) | Native consequence of the record lowering: the field is non-optional, so the read is non-optional. |
| **T7** (optional-key access) | `p["k"]` on a `total=False`/`NotRequired` key yields `Optional[T]` | The field's type IS `Optional[T]` (a `_union_*` variant with a `None` arm); the read yields the variant type, and the program must narrow (reusing the TY1 Union `is None` match lowering) before dereferencing the payload. |
| **T8** (typed construction) | `{"x": 1, "y": 2}` assignable to `Point` iff keys/types match | The dict-literal emitter recognizes a TypedDict-typed construction context and emits a record literal `{ x = 1; y = 2 }`; Why3 type-checks each field's value against the declared type and rejects missing/extra fields natively (record literals must provide every field, in declaration order). |
| **T9** (missing/extra keys rejected) | missing required key / extra key is a static error | Native Why3 record-literal type-checking: a literal missing a field or with an extra field is a type error. |

### 2.3 The lowering seam (concrete file changes)

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/preamble.py` | **No new path.** The existing record-type emission (`:2830`) handles TypedDict records. Confirm `is_typeddict` records emit a plain `type point = { x: int; y: int }` with no class invariant (they have none). |
| `src/pycsl/module6_whyml/expressions.py` | add `_typeddict_field_access(value, index_ir, ...)` invoked from `_handle_subscript` (`:2151`): if `value` is a `Var` whose symbol-table entry is a TypedDict record name AND `index_ir` is a `Constant` string matching a declared field, emit `p.<field_label>` via the existing `_field_label`. Falls through to the existing subscript paths for non-TypedDict receivers (byte-identical). |
| `src/pycsl/module6_whyml/expressions.py` | add `_typeddict_record_literal(dict_ir, target_type, ...)` invoked from the dict-literal emission path: if the construction context is a TypedDict record type, emit `{ x = <v0>; y = <v1> }` in declaration order. Falls through for non-TypedDict dict literals (byte-identical). |
| `src/pycsl/core_ir_semantic.py` | add `_check_typeddict_access(func)`: for every `Subscript` whose receiver is a TypedDict-record-typed variable, require the index to be a string-literal Constant matching a declared field. A non-literal or unknown-key access is a static error (T5). |

---

## 3. Shim contract (runtime plane: `src/pycsl_lib/typ/__init__.py`)

Per the two-plane spec §2 (R1–R8) and the no-blend rule (D4), the runtime shim exposes the
introspectable `TypedDict` class object and performs **NO validation**. The current
`src/pycsl_lib/typ/__init__.py` already shims `cast`/`Union`/`Literal`/`Final`/`NoReturn`;
`TypedDict` follows the same discipline.

### 3.1 Shim surface

```python
# In src/pycsl_lib/typ/__init__.py — TypedDict alias construction, Shimmed (R1–R8).

#@ ensures \result == val
def TypedDict(typename, fields, val) -> int:
    return val
```

(The `-> int` return tag and `val` parameter are the existing PyCSL convention for opaque
runtime objects — the same convention `cast`/`Union`/`Literal` use. The WhyML model is
`int`-typed and the runtime object is opaque to the verifier; this is the established
Modelled-for-identity pattern. The `val` parameter carries the identity postcondition.)

### 3.2 Contract discharges each R-clause

| R-clause | How the shim honours it |
|---|---|
| R1 (plain dict instance) | The shim does NOT construct dict instances — it exposes the `TypedDict` class object. Instances are constructed by the program's dict literals (`{"x": 1}`), which are plain dicts at runtime (S4). The shim's responsibility is the class object only. |
| R2 (introspection) | `get_type_hints`/`get_origin`/`get_args` (already shimmed at `:46`–`:57`) return introspection-only values. **No change to those functions.** |
| R3 (no enforcement) | The shim's `#@ ensures \result == val` carries ONLY the identity postcondition. There is no `requires` on the field types. |
| R4 (no isinstance against TypedDict) | The shim does NOT make `TypedDict` a valid `isinstance` second argument. This is a runtime property of the class object, not something the shim enforces — the class object raises `TypeError` natively (S4: `_TypedDictMeta.__instancecheck__`). |
| R5 (subscript is dict subscript) | The shim does NOT intercept `p["x"]` — that is a plain dict subscript on a plain dict instance, native CPython behaviour. The static plane's record-field read lowering is invisible at runtime. |
| R6 (no key/type check on subscript) | Same as R5 — the runtime does not check; the shim does not check. |
| R7 (no validation in the shim) | The shim performs NO check on whether a value has the declared keys/types. A shim that DID check would be unfaithful in exactly the way an over-strong axiom is (D4). |
| R8 (plain-dict alias) | The runtime plane of a TypedDict-typed value is the plain-dict plane; the shim's only job is the class object. |

### 3.3 Why the runtime shim does NOT discharge any static clause

This is the no-blend rule (D4) made concrete: the shim's `ensures \result == val` is
SATISFIED by every value regardless of type. The static clauses T2–T9 are discharged by
Why3 record-type-checking (§2.2), which is invisible to the shim. A conformance-agent
authoring the S5 subset from the two-plane spec + the shim surface alone cannot
reverse-engineer the lowering — the independence-based Gate C (c) holds.

---

## 4. Classification (`--soundness-report`)

Per the two-plane spec §4, the classification is **dual** (both planes, separately):

| Plane | Classification | Tag |
|---|---|---|
| Static | **Interpreted** | the class declaration is consumed by the static plane and lowered to a record type_decl with field-access/construction obligations (per §2.2) |
| Runtime | **Shimmed** | the runtime meaning is the plain-dict alias + introspectable class object, no enforcement (per §3) |

### 4.1 GT gap codes tagged for `TypedDict`

- **GT7** (analogous, NOT a new code) — D3 documents the `isinstance`-against-TypedDict
  asymmetry: the static T2 record-shape obligation must NOT be discharged by any runtime
  `isinstance`/presence check (R4 raises `TypeError`; even `"x" in p` is the dict-plane
  behaviour, not the static record-shape judgment). Tagged in the report as a
  `no_blend_typeddict_isinstance` note.
- **GT8** — the S5 conformance subset for `TypedDict` is the conformance-agent's standing
  artifact (NOT this DRAFT's deliverable). Each clause T2–T9 above names the S5 case shape
  it commits to.

No other GT gap is tagged for `TypedDict` at TY2. A future TY2 enhancement
(cross-TypedDict structural subtyping) is flagged as `GT-T2-future` (out of scope for this
delivery).

---

## 5. Standing gate plan (total additivity)

Per `typing-global-impl.md` §4 Gate B and the core-agent's hard rules:

### 5.1 Byte-identical emission for unaffected drivers

- The `_is_typeddict_class` check is a pure base-name test: for any class that does NOT
  have `TypedDict` in its bases, `visit_ClassDef` proceeds exactly as before. Every
  non-TypedDict driver produces byte-identical IR and byte-identical WhyML.
- The `_handle_subscript` TypedDict-field check fires only when the receiver's
  symbol-table type is a TypedDict record (i.e. `is_typeddict: True`); every non-TypedDict
  subscript falls through to the existing array/dict/opaque paths unchanged.
- The dict-literal TypedDict-record check fires only when the construction target type is a
  TypedDict record; every non-TypedDict dict literal falls through unchanged.
- The corpus byte-diff gate (`bin/run-reference-tests.sh` / the standing gate) MUST remain
  green for every non-TypedDict driver. A byte-diff on an unaffected driver is a
  regression.

### 5.2 `os` proof + `formal_<name>` suite re-confirmed

- The `os` library (now fully green) does NOT use `TypedDict` in its verified surface —
  confirm by `rg 'TypedDict' src/pycsl_lib/os/` before claiming additivity. (Expected: zero
  matches in verified code; any match is a comment-only reference.)
- The `formal_<name>` suite (json, re, warnings, …) is re-run; every previously-green
  formal test MUST remain green.

### 5.3 IR-conformance corpora

- **No IR_VERSION bump.** The TypedDict construct reuses the EXISTING `type_decl` (record)
  IR node and adds ONE optional boolean field `is_typeddict` (defaults `False`). The IR
  schema is backward-compatible: `type_decl.get("is_typeddict", False)` reads as `False`
  for every pre-existing record. `IR_VERSION` stays at its current value;
  `ACCEPTED_IR_VERSIONS` is unchanged. The IR-conformance corpora (core + front-end
  `*.ir.json` / `*.expected.mlw`) MUST remain green unchanged for every non-TypedDict
  driver.
- The `is_typeddict` field is documented in `docs/ir.md` per its §10 process as a
  non-versioned additive field (STILL no IR_VERSION bump, because the schema is
  backward-compatible — old consumers ignore the field).

### 5.4 doc-coherency green

- `test-suite/annotations.md`: add the canonical entry for the `TypedDict` annotation
  surface (citing S2 PEP 589 / PEP 655). Per `pycsl-doc-coherency` skill, the entry must
  also appear in `docs/pycsl-concrete-syntax-reference.md`,
  `docs/pycsl-static-semantics-reference.md`, `docs/pycsl-translational-reference.md`, and a
  `config/skills/` skill (likely `pycsl-annotate`). `bin/doc-coherency.py --check` MUST
  remain green.

### 5.5 Non-vacuity gate

- The TypedDict VCs (T5 field-access type-checking, T8 record-literal type-checking) are
  native Why3 type-checking goals, NOT separate `goal` VCs — they are non-vacuous by
  construction (Why3 rejects ill-typed programs). The `--check-vacuity` gate is green
  trivially (no new `goal` VCs to test). A false-twin on a TypedDict field-access (e.g.
  asserting `p.x == <impossible>`) MUST FAIL the type-check — confirming the field read is
  real.

---

## 6. NoReturn × vacuity gate

**N/A for `TypedDict`.** The NoReturn × vacuity interaction is owned by the `NoReturn`
construct's spec. `TypedDict` does not interact with the vacuity gate in the
NoReturn-specific way: a TypedDict field of type `NoReturn` would be a divergent field
(never constructible), flagged in `core_ir_semantic` as a warning (a dead-field property),
NOT a vacuity failure.

---

## 7. Deliverable checklist (on APPROVAL)

- [x] Front-end: `_is_typeddict_class`, `_collect_typeddict_fields` (renamed
      `_emit_typeddict_record`), `_collect_typeddict_functional` (renamed
      `_synthesize_typeddict_functional`) in `Module5_IREmitter.py`; dispatch
      from `visit_ClassDef` and `visit_Module`.
- [x] Module 6: `_typeddict_field_access` in `expressions.py` (invoked from
      `_handle_subscript`); `_typeddict_record_literal` in `expressions.py`
      (invoked from the `DictLit` path). GAP-001 fix: missing/extra keys now
      raise `PYCSL-SEM-TYPEDDICT-MISSING-KEY` / `PYCSL-SEM-TYPEDDICT-EXTRA-KEY`.
- [x] `core_ir_semantic.py`: `_check_typeddict_access` (T5 literal-key
      requirement).
- [x] `src/pycsl_lib/typ/__init__.py`: `TypedDict` shim (identity
      `ensures \result == val`).
- [x] `test-suite/annotations.md` (§12.12) + three reference docs; doc-coherency
      green.
- [x] `--soundness-report`: `TypedDict` classified Interpreted (static) /
      Shimmed (runtime), GT7-analog note documented.
- [x] Standing gate: corpus byte-diff green for non-TypedDict drivers (80/80 +
      IR-conformance 38 OK / 0 MISMATCH); `os` proof SUCCESS; formal suite
      (formal_zl, formal_hq) SUCCESS; NO IR_VERSION bump; `--check-vacuity`
      green on both new TypedDict VCs.
- [x] NO conformance-suite or shim-faithfulness-driver edits beyond the
      conformance-agent's own artifacts (T5/T8/T9/T5b/R3/R7 + GAP-001 +
      GATE-C-RESULTS).

---

## 8. Open questions for the coordinator (editorial)

1. **Functional form scope.** This DRAFT commits to recognizing the class form
   (`class Point(TypedDict)`) as the primary surface and the functional form
   (`Point = TypedDict("Point", {...})`) as a best-effort literal-only fallback. Confirm
   the coordinator accepts that a non-literal functional form is a byte-identical fallback
   (no record synthesized) rather than a hard error.
2. **`is_typeddict` IR field.** Is the optional `is_typeddict: True` flag on the record
   `type_decl` acceptable, or should the TypedDict-ness be inferred from the absence of
   `__init__` + presence of class-body AnnAssigns (inference-only, no IR field)?
   (Recommendation: explicit flag — it is load-bearing for Module 6's subscript dispatch
   and the no-blend check; inference is fragile.)
3. **Cross-TypedDict structural subtyping (T2b).** This DRAFT limits T2 to same-named
   assignability. Cross-TypedDict structural subtyping (a TypedDict with a superset of
   keys assignable to one with a subset) is flagged as `GT-T2-future`. Confirm the
   coordinator accepts this scope boundary for TY2.
