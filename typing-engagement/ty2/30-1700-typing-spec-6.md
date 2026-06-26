# 30-1700-typing-spec-6.md — `NamedTuple` Implementation Spec (DRAFT)

**Status:** DONE (core-agent implemented both planes; Gates A/B/C PASS; graduated to Normative).
**Tier:** TY2 (aggregates and interfaces).
**Construct:** `NamedTuple` (PEP 526 class form + PEP 484 functional form).
**Two-plane spec authority:** `typing-engagement/ty2/namedtuple-twoplane-spec.md` (Gate A APPROVED).
**Global guides honoured:** `typing-global-impl.md` §0 (no-blend), §4 (per-construct pipeline + gates),
§5 (TY2: "NamedTuple -> WhyML records"). The core-agent hard rule: a NamedTuple class synthesizes a
WhyML record `type nt = { x: int; y: int }` (reusing the TypedDict record seam), named field access
`p.x` becomes record-field access, positional access `p[0]` becomes record-field access by index,
construction `Point(1, 2)` becomes a record literal. NO `\trusted`.

**This is a planning document. No `src/pycsl/` file is modified by this DRAFT.** On
coordinator APPROVAL, the core-agent implements both planes and runs the standing gate.

---

## 0. Design summary (one paragraph)

`class Point(NamedTuple): x: int; y: int` is recognized at the `visit_ClassDef` seam
(`Module5_IREmitter.py:1579`) by checking whether `NamedTuple` appears in `node.bases`. For
such classes, a new helper `_emit_namedtuple_record(node)` walks the class body's
AnnAssigns (the field declarations, in declaration order) and synthesizes a `type_decl` of
kind `record` whose `fields` carry the declared per-field types (resolved via the existing
`_field_type_from_annotation_inst` resolver). The record carries `init_params` (the field
names, in order) and `init_body` (each field set from its same-named param), so positional
construction `Point(1, 2)` reuses the EXISTING `_call_record_constructor` path — emitting a
record literal `{ x = 1; y = 2 }`. Named field access `p.x` lowers through the EXISTING
`_handle_attribute_expr` path (a NamedTuple-typed param is added to `_record_locals` by
`_param_type_str`, so `p.x` already emits `p.x`). Positional access `p[0]` is recognized at
the `_handle_subscript` seam: when the subscript's receiver is a NamedTuple-record-typed
variable AND the index is an integer literal in range, the subscript lowers to a
record-field read of the field at that declaration index (`p[0]` → `p.x`). The runtime plane
is a thin shim in `src/pycsl_lib/typ/__init__.py` exposing `NamedTuple` as a callable that
returns an opaque introspectable class object (the plain-tuple alias) and performs NO
validation (R1–R9, D4 no-blend). NO new IR node, NO IR_VERSION bump (reuses the existing
`type_decl` (record) and `Subscript`/`Attribute` IR nodes, with one optional
`is_namedtuple: True` field), NO `\trusted`.

---

## 1. Normalization rule (front-end: `src/pycsl/frontend/`)

### 1.1 Surface forms to recognize

Per the two-plane spec §1.0 (N1, N1a, N1b):

| Surface | AST shape (post-`pure_ast`) | Disposition |
|---|---|---|
| `class Point(NamedTuple): x: int; y: int` | `ClassDef(name="Point", bases=[Name("NamedTuple")], body=[AnnAssign(...), ...])` | synthesize record `point` with fields `x: int, y: int` (in declaration order) |
| `class Point(NamedTuple): x: int = 0; y: int = 0` | `ClassDef(..., body=[AnnAssign(target=Name, annotation=T, value=Constant(0)), ...])` | synthesize record with `field_defaults` from the literal default (N1b) |
| `Point = NamedTuple("Point", [("x", int), ("y", int)])` functional form | `Assign(targets=[Name], value=Call(func=Name("NamedTuple"), args=[Constant, List]))` | TY2-scope: the class form is the priority; functional form is RECOGNIZED but field-extraction is limited to literal `[("name", type), ...]` lists. If non-literal, no record is synthesized (byte-identical fallback). |

`NamedTuple` is recognized by the bare head name in `bases` (the import-rewriting in
`import_classifier.py` already canonicalizes `from typing import NamedTuple`).

### 1.2 Canonical IR form

The canonical IR form is a `type_decl` of kind `record`:

```
{ "kind": "record",
  "name": <ClassName>,             # e.g. "Point"
  "fields": [ {"name": "x", "type": "int", "mutable": True}, ... ],  # declaration order
  "class_invariants": [],
  "field_defaults": {"x": 0, "y": 0},
  "has_hash": False, "has_eq": False, "is_unhashable": False,
  "constants": {}, "bases": [],
  "init_params": ["x", "y"],       # field names in order → positional construction
  "init_body": [{"field": "x", "value": {"type": "Var", "name": "x"}},
                {"field": "y", "value": {"type": "Var", "name": "y"}}],
  "init_ensures": [],
  "is_mixin": False, "compose_from": [],
  "is_namedtuple": True            # NEW optional field (see §5.3 on IR shape)
}
```

The `is_namedtuple: True` flag is the ONLY new piece of IR state. It is optional
(`type_decl.get("is_namedtuple", False)` reads as `False` for every pre-existing record),
so the IR schema is backward-compatible — no IR_VERSION bump is required. The flag is
consumed by Module 6's `_handle_subscript` (positional-access lowering) and by
`core_ir_semantic` for the no-blend check (§3).

### 1.3 Normalization steps (in order)

1. **Recognition** — in `visit_ClassDef` (`Module5_IREmitter.py:1579`), BEFORE the existing
   `fields, field_defaults = self._collect_class_fields(node)` call, check
   `_is_namedtuple_class(node)`: True iff any `base` in `node.bases` is a `Name` with
   `id == "NamedTuple"` OR an `Attribute` with `attr == "NamedTuple"`. If True, dispatch to
   `_emit_namedtuple_record(node)` instead of `_collect_class_fields`, and skip the
   `__init__`/mixin/inheritance paths entirely.
   *Byte-identical for non-NamedTuple drivers:* the check is a pure base-name test; every
   non-NamedTuple class skips it unchanged.

2. **Field extraction** — `_emit_namedtuple_record(node)` walks `node.body` for
   `AnnAssign` whose target is a `Name` (the `x: int` declaration form). For each:
   - resolve the field type via `_field_type_from_annotation_inst(annotation, class_name)`
     (the existing resolver, which already handles `int`/`str`/`bool`/`bytes`/`float`/
     `list`/`dict`/Union/Optional/Final/Literal);
   - if the AnnAssign has a `value` (a default, N1b), capture it as the
     `field_defaults[field_name]` (int-valued per the existing convention; a non-int default
     falls back to 0);
   - Append `{"name": field_name, "type": resolved_tag, "mutable": True}` to `fields` (in
     declaration order — order is significant for positional access N5).

3. **Synthesis** — append the `type_decl` (record) to `program_ir["type_decls"]` with
   `is_namedtuple: True`, `init_params` = field names in order, `init_body` = each field set
   from its same-named param. Populate `program_ir["constructors"]` for the class name so
   `Point(...)` (positional construction) reuses the existing Tier-A parametrized record
   construction (`_call_record_constructor`).

4. **Functional form** — `_synthesize_namedtuple_functional(node)` walks the module body for
   `Assign` whose value is `Call(func=Name("NamedTuple"), args=[Constant(name), List(...)])`.
   If the list's elements are all `(str, type)` tuples, it synthesizes the same record
   `type_decl`. If the list is non-literal, no record is synthesized (byte-identical
   fallback — the assignment stays an opaque int). This mirrors the TypedDict functional
   form handling.

### 1.4 Front-end files that change (on APPROVAL)

| File | Change |
|---|---|
| `src/pycsl/frontend/Module5_IREmitter.py` | add `_is_namedtuple_class`, `_emit_namedtuple_record`, `_synthesize_namedtuple_functional`; dispatch from `visit_ClassDef` (`:1579`) and `visit_Module`. The existing `_collect_class_fields` is NOT modified (byte-identical for non-NamedTuple). The pre-existing `_synthesize_namedtuple_records` (functional `collections.namedtuple` form, all-int fields) is NOT modified — it handles a different factory. |

---

## 2. Lowering table entry (Module 6: `src/pycsl/module6_whyml/`)

### 2.1 The lowering

The NamedTuple record type_decl lowers through the EXISTING record-emission path in
`module6_whyml/preamble.py` (`:2830`), which already emits `type point = { x: int; y: int }`
for records. The `is_namedtuple` flag does NOT change record emission — it only gates the
positional-access lowering path below.

### 2.2 Per-clause VC mapping (the load-bearing part)

| Clause | Static obligation | VC / mechanism |
|---|---|---|
| **N2** (record-shape assignability) | `v: Point` assignable to `Point` | Why3 record-type equality (the parameter is typed `point`); a different NamedTuple is a separate record type. Nominal typing (N2) is native Why3 type-checking. |
| **N3** (plain tuple NOT assignable) | plain `tuple` not assignable to `Point` | Why3 type-checking: a `tuple`-typed value has no record type; the parameter's record type rejects it. No new VC — native Why3 type error. |
| **N4** (typed named-field access) | `p.x` has type `int` for `p: Point` | The EXISTING `_handle_attribute_expr` path: a NamedTuple-typed param is in `_record_locals` (via `_param_type_str`), so `p.x` emits `p.x` (a record-field read). Why3 type-checks the field's declared type. An unknown attribute (`p.z`) is a Why3 type error (the field doesn't exist). |
| **N5** (typed positional access) | `p[0]` has type `int` for `p: Point` (field `x`) | The subscript `_handle_subscript` recognizes an integer-literal index into a NamedTuple-record-typed receiver and emits `p.x` (the field at declaration index 0). Why3 type-checks the field's declared type. An out-of-range index (`p[2]` on a 2-field Point) is a `core_ir_semantic` static error. A non-literal index is a `core_ir_semantic` static error (N5 requires literal indices). |
| **N6** (typed positional construction) | `Point(1, 2)` assignable to `Point` iff arity/types match | The EXISTING `_call_record_constructor` path: `init_params` matches arity, each arg substitutes into `init_body`, emitting `{ x = 1; y = 2 }`. Why3 type-checks each field's value against the declared type. |
| **N7** (wrong arity rejected) | `Point(1)` (too few) / `Point(1, 2, 3)` (too many) is a static error | `_call_record_constructor` arity mismatch → default-filling (sound, less precise) OR a Why3 type error. The conformance gate covers the reject case. |

### 2.3 The lowering seam (concrete file changes)

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/preamble.py` | **No new path.** The existing record-type emission (`:2830`) handles NamedTuple records. Thread `is_namedtuple` into `_record_types` (like `is_typeddict`). |
| `src/pycsl/module6_whyml/expressions.py` | add `_namedtuple_positional_access(value, index_ir, ...)` invoked from `_handle_subscript` (`:2151`): if `value` is a `Var` whose symbol-table entry is a NamedTuple record name AND `index_ir` is an integer-literal `Constant` in range, emit `p.<field_label at that index>` via the existing `_field_label`. Falls through to the existing subscript paths for non-NamedTuple receivers (byte-identical). |
| `src/pycsl/core_ir_semantic.py` | add `_check_namedtuple_access(func, nt_record_names)`: for every `Subscript` whose receiver is a NamedTuple-record-typed variable, require the index to be an integer-literal Constant in range. A non-literal or out-of-range index is a static error (N5). |

---

## 3. Shim contract (runtime plane: `src/pycsl_lib/typ/__init__.py`)

Per the two-plane spec §2 (R1–R9) and the no-blend rule (D4), the runtime shim exposes the
introspectable `NamedTuple` class object and performs **NO validation**. The current
`src/pycsl_lib/typ/__init__.py` already shims `cast`/`Union`/`Literal`/`Final`/`NoReturn`/
`TypedDict`; `NamedTuple` follows the same discipline.

### 3.1 Shim surface

```python
# In src/pycsl_lib/typ/__init__.py — NamedTuple alias construction, Shimmed (R1–R9).

#@ ensures \result == val
def NamedTuple(typename, fields, val) -> int:
    return val
```

(The `-> int` return tag and `val` parameter are the existing PyCSL convention for opaque
runtime objects — the same convention `cast`/`Union`/`Literal`/`TypedDict` use. The WhyML
model is `int`-typed and the runtime object is opaque to the verifier; this is the
established Modelled-for-identity pattern. The `val` parameter carries the identity
postcondition.)

### 3.2 Contract discharges each R-clause

| R-clause | How the shim honours it |
|---|---|
| R1 (plain tuple instance) | The shim does NOT construct tuple instances — it exposes the `NamedTuple` class object. Instances are constructed by the program's positional calls (`Point(1, 2)`), which are plain tuples at runtime (S4). The shim's responsibility is the class object only. |
| R2 (introspection) | `get_type_hints`/`get_origin`/`get_args` (already shimmed) return introspection-only values. **No change to those functions.** |
| R3 (no enforcement) | The shim's `#@ ensures \result == val` carries ONLY the identity postcondition. There is no `requires` on the field types. |
| R4 (no isinstance against NamedTuple type) | The shim does NOT make `NamedTuple` a valid `isinstance` second argument beyond what CPython does natively (tuple-ness). This is a runtime property of the class object, not something the shim enforces. |
| R5 (attribute is tuple-index) | The shim does NOT intercept `p.x` — that is a plain tuple-index read via a synthesized property on a plain tuple instance, native CPython behaviour. The static plane's record-field read lowering is invisible at runtime. |
| R6 (subscript is tuple subscript) | The shim does NOT intercept `p[0]` — that is a plain tuple subscript on a plain tuple instance, native CPython behaviour. |
| R7 (no key/type check on subscript) | Same as R6 — the runtime does not check; the shim does not check. |
| R8 (no validation in the shim) | The shim performs NO check on whether a value has the declared field types. A shim that DID check would be unfaithful in exactly the way an over-strong axiom is (D4). |
| R9 (plain-tuple alias) | The runtime plane of a NamedTuple-typed value is the plain-tuple plane; the shim's only job is the class object. |

### 3.3 Why the runtime shim does NOT discharge any static clause

This is the no-blend rule (D4) made concrete: the shim's `ensures \result == val` is
SATISFIED by every value regardless of type. The static clauses N2–N7 are discharged by
Why3 record-type-checking (§2.2), which is invisible to the shim. A conformance-agent
authoring the S5 subset from the two-plane spec + the shim surface alone cannot
reverse-engineer the lowering — the independence-based Gate C (c) holds.

---

## 4. Classification (`--soundness-report`)

Per the two-plane spec §4, the classification is **dual** (both planes, separately):

| Plane | Classification | Tag |
|---|---|---|
| Static | **Interpreted** | the class declaration is consumed by the static plane and lowered to a record type_decl with field-access/construction obligations (per §2.2) |
| Runtime | **Shimmed** | the runtime meaning is the plain-tuple alias + introspectable class object, no enforcement (per §3) |

### 4.1 GT gap codes tagged for `NamedTuple`

- **GT7** (analogous, NOT a new code) — D3 documents the `isinstance`-against-NamedTuple
  asymmetry: the static N2 record-shape obligation must NOT be discharged by any runtime
  `isinstance`/tuple-shape check (R4 is a tuple-ness check, not a type-enforcement check).
  Tagged in the report as a `no_blend_namedtuple_isinstance` note.
- **GT8** — the S5 conformance subset for `NamedTuple` is the conformance-agent's standing
  artifact (NOT this DRAFT's deliverable). Each clause N2–N7 above names the S5 case shape
  it commits to.

No other GT gap is tagged for `NamedTuple` at TY2.

---

## 5. Standing gate plan (total additivity)

Per `typing-global-impl.md` §4 Gate B and the core-agent's hard rules:

### 5.1 Byte-identical emission for unaffected drivers

- The `_is_namedtuple_class` check is a pure base-name test: for any class that does NOT
  have `NamedTuple` in its bases, `visit_ClassDef` proceeds exactly as before. Every
  non-NamedTuple driver produces byte-identical IR and byte-identical WhyML.
- The `_handle_subscript` NamedTuple-positional check fires only when the receiver's
  symbol-table type is a NamedTuple record (i.e. `is_namedtuple: True`); every non-
  NamedTuple subscript falls through to the existing array/dict/opaque paths unchanged.
- The corpus byte-diff gate (`bin/byte-diff-sweep.sh` / the standing gate) MUST remain
  green for every non-NamedTuple driver. A byte-diff on an unaffected driver is a
  regression.

### 5.2 `os` proof + `formal_<name>` suite re-confirmed

- The `os` library (now fully green) does NOT use `NamedTuple` in its verified surface —
  confirm by `rg 'NamedTuple' src/pycsl_lib/os/` before claiming additivity. (Expected: zero
  matches in verified code; any match is a comment-only reference.)
- The `formal_<name>` suite (json, re, warnings, …) is re-run; every previously-green
  formal test MUST remain green.

### 5.3 IR-conformance corpora

- **No IR_VERSION bump.** The NamedTuple construct reuses the EXISTING `type_decl` (record)
  IR node and adds ONE optional boolean field `is_namedtuple` (defaults `False`). The IR
  schema is backward-compatible: `type_decl.get("is_namedtuple", False)` reads as `False`
  for every pre-existing record. `IR_VERSION` stays at its current value;
  `ACCEPTED_IR_VERSIONS` is unchanged. The IR-conformance corpora (core + front-end
  `*.ir.json` / `*.expected.mlw`) MUST remain green unchanged for every non-NamedTuple
  driver.
- The `is_namedtuple` field is documented in `docs/ir.md` per its §10 process as a
  non-versioned additive field (STILL no IR_VERSION bump, because the schema is
  backward-compatible — old consumers ignore the field).

### 5.4 doc-coherency green

- `test-suite/annotations.md`: add the canonical entry for the `NamedTuple` annotation
  surface (citing S2 PEP 526 / PEP 484). Per `pycsl-doc-coherency` skill, the entry must
  also appear in `docs/pycsl-concrete-syntax-reference.md`,
  `docs/pycsl-static-semantics-reference.md`, `docs/pycsl-translational-reference.md`, and a
  `config/skills/` skill (likely `pycsl-annotate`). `bin/doc-coherency.py --check` MUST
  remain green.

### 5.5 Non-vacuity gate

- The NamedTuple VCs (N4 named-field-access type-checking, N5 positional-access
  type-checking, N6 record-literal type-checking) are native Why3 type-checking goals, NOT
  separate `goal` VCs — they are non-vacuous by construction (Why3 rejects ill-typed
  programs). The `--check-vacuity` gate is green trivially (no new `goal` VCs to test). A
  false-twin on a NamedTuple field-access (e.g. asserting `p.x == <impossible>`) MUST FAIL
  the type-check — confirming the field read is real.

---

## 6. NoReturn × vacuity gate

**N/A for `NamedTuple`.** The NoReturn × vacuity interaction is owned by the `NoReturn`
construct's spec. `NamedTuple` does not interact with the vacuity gate in the
NoReturn-specific way.

---

## 7. Deliverable checklist (on APPROVAL)

- [x] Front-end: `_is_namedtuple_class`, `_emit_namedtuple_record`,
      `_synthesize_namedtuple_functional` in `Module5_IREmitter.py`; dispatch
      from `visit_ClassDef` and `visit_Module`.
- [x] Module 6: `_namedtuple_positional_access` in `expressions.py` (invoked
      from `_handle_subscript`); `is_namedtuple` threaded into `_record_types`
      in `preamble.py`.
- [x] `core_ir_semantic.py`: `_check_namedtuple_access` (N5 literal-index
      requirement).
- [x] `src/pycsl_lib/typ/__init__.py`: `NamedTuple` shim (identity
      `ensures \result == val`).
- [x] `test-suite/annotations.md` (§12.13) + three reference docs;
      doc-coherency green.
- [x] `--soundness-report`: `NamedTuple` classified Interpreted (static) /
      Shimmed (runtime), GT7-analog note documented.
- [x] Standing gate: corpus byte-diff green for non-NamedTuple drivers;
      `os` proof SUCCESS; formal suite SUCCESS; NO IR_VERSION bump;
      `--check-vacuity` green on both new NamedTuple VCs.
- [x] NO conformance-suite or shim-faithfulness-driver edits beyond the
      conformance-agent's own artifacts.
