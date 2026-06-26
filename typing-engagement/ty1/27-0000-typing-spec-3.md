# 27-0000-typing-spec-3.md — `Final` Implementation Spec (DRAFT → DONE)

**Status:** DONE (core-agent implemented both planes; standing gate green).
**Tier:** TY1 (monomorphic refinements).
**Construct:** `Final` (PEP 591 `Final[T]` / bare `Final`).
**Two-plane spec authority:** `typing-engagement/ty1/final-twoplane-spec.md` (APPROVED).
**Global guides honoured:** `typing-global-impl.md` §0/§5 ("Final as degenerate HAPPY"),
§4 (per-construct pipeline + gates); `docs/typing-global-overview.md` §4.2 (TY1 lowering
locus = front-end normalization + `core_ir_semantic` static-semantics seam).
**Sound expressibility reminder (overview §2.1):** the IR/WhyML lower bound may be STRICTER
than S1, never weaker. `Final` is fully sound — the write-restriction is a syntactic
write-site check (decidable by construction), so NO GT gap is tagged for it (two-plane
spec §4).
**No-blend reminder (overview §2.3 / FD2):** the static-plane write-policy check (§1 of
the two-plane spec) and the runtime-plane alias-object/no-enforcement behaviour (§2 of
the two-plane spec) are carried as SEPARATE contracts. The runtime shim must NOT
introduce a descriptor that enforces the write-restriction (FR6) — that would blend the
planes.

**This is a planning document.** On coordinator APPROVAL, the core-agent implements both
planes and runs the standing gate.

---

## 0. Design summary (one paragraph)

`Final[T]` is **lowered at the front-end normalization seam** to the degenerate
single-attribute, single-writer form of HAPPY's no-write confinement: a per-module
**final registry** records each Final-annotated name and its *allowed writer* (the
declaration site for module/class-level Final — F1; the declaring class's `__init__` for
instance-attribute Final — F2). The annotation's *type* is the inner type `T` (F3 — no
narrowing): `_normalize_final_annotation` recognizes `Final[T]` (Subscript value=Name
"Final") and bare `Final` (Name "Final"), returns `T`'s IR type tag, and records the
name in the registry. **NO new IR node is introduced, NO IR_VERSION bump is required, NO
new VC kind is introduced** — the write-policy is a *static-semantics check* in
`core_ir_semantic._check_final`, not a VC. The runtime plane is a thin shim in
`src/pycsl_lib/typ/__init__.py` that constructs the introspectable `typing.Final` alias
object and performs NO validation (FR1–FR6) — explicitly NOT a write-guard descriptor.

### 0.1 Why degenerate HAPPY (and not a new mechanism)

HAPPY's no-write confinement is a meta-pass that enforces "no attribute is written
outside its allowed writer-set" (§1.5 of the two-plane spec, F4). `Final` is the
single-attribute, single-writer special case: one name (F1) or one `self.attr` (F2), one
allowed writer. Reusing HAPPY's *pattern* (a syntactic write-site check over the IR
body) — NOT HAPPY's IR blob or meta-pass machinery — keeps `Final` additive: no new IR
field carries the policy (the registry is a front-end-collected list plumbed as
`program_ir["final_registry"]`, an additive metadata key Module 6 ignores), and the
check is a read-only IR walk in `core_ir_semantic`. This is the divergence the spec-agent
named (FD1: "static write-restriction vs runtime no-enforcement"): the static plane is a
write-site check; the runtime plane is an alias object that enforces nothing.

### 0.2 What is NOT introduced

- **No new IR node.** `Final` reuses the existing `Assign` / `AugAssign` / `FieldAssign`
  / `FieldAugAssign` statement nodes (the write sites the check inspects) and the
  existing `symbol_table` type-tag field (the annotation's inner type). The final
  registry is an additive module-level metadata key (`program_ir["final_registry"]`),
  NOT a per-statement or per-node IR field — Module 6 ignores it, so emission is
  byte-identical for every driver.
- **No IR_VERSION bump.** The IR schema is unchanged. `IR_VERSION` stays at its current
  value; `ACCEPTED_IR_VERSIONS` is unchanged. The IR-conformance corpora (core +
  front-end `*.ir.json` / `*.expected.mlw`) MUST remain green unchanged for every
  non-Final driver.
- **No new VC kind.** The write-policy check is a *semantic check*
  (`core_ir_semantic._check_final`), not a Why3 goal. It raises `PyCSLSemanticError` on
  a violation, exactly as `_check_happy` / `_check_concurrency` do. No `_emit_*_vc`
  helper is added.
- **No new `Module 6` path.** Module 6 is unchanged — the inner type `T` flows through
  the existing `_param_type_str` / `_field_type_from_annotation` resolution; no
  synthesized contract is emitted (F3 is the *absence* of narrowing — there is nothing
  to synthesize).
- **No runtime enforcement.** The shim is identity (`ensures \result == val`), NOT a
  descriptor. A write-guard descriptor would blend the planes (FR6 / FD2).

---

## 1. Normalization rule (front-end: `src/pycsl/frontend/Module5_IREmitter.py`)

### 1.1 Surface forms to recognize

Per the two-plane spec §1.1 (F1), §1.2 (F2/F2a), and §1.3 (F3), TWO surface forms denote
the `Final` static write-restriction:

| Surface | AST shape (post-`pure_ast`) | Canonical spelling |
|---|---|---|
| `Final[T]` | `Subscript(value=Name(id="Final"), slice=T)` | `final` (registry entry; type tag = τ(T)) |
| `Final` (bare) | `Name(id="Final")` | `final` (registry entry; type tag = `Any`) |

`typing.Final` is recognized by the bare head name (the import-rewriting in
`import_classifier.py` already canonicalizes `from typing import Final`). PEP 591 forbids
nested `Final` (`Final[Final[int]]`); a nested form falls through to the legacy
parametric resolution (`head.lower()` → `"final"` on the outer head) and is NOT
registered — it carries no write-policy (a documented strictness: the inner `Final` is
ignored, matching S7's pre-existing behaviour for unrecognised parametric annotations).

### 1.2 Canonical IR form

The canonical IR form is the **inner type tag** (`τ(T)`) in the symbol_table / field
type, PLUS a per-module **final registry** entry recording the name and its allowed
writer:

```
# For `x: Final[int] = 5` at module scope:
#   module_constants["x"] = 5         # the existing module-constant path (unchanged)
#   final_registry.append({"name": "x", "kind": "module", "class": None,
#                          "allowed_writer": None})   # F1: declaration is the only write

# For `attr: Final[int]` in class C's body (instance attribute):
#   fields.append({"name": "attr", "type": "int", "mutable": True})   # existing field path
#   final_registry.append({"name": "attr", "kind": "class_attr", "class": "C",
#                          "allowed_writer": "__init__"})   # F2: __init__-only writes
```

The inner type tag `τ(T)` is resolved by the EXISTING `_m5_get_type_name_legacy` on the
slice (`Final[int]` → `"int"`, `Final[str]` → `"str"`, `Final[MyClass]` → `"myclass"`).
For bare `Final` (no slice), the type tag is `"Any"` (the legacy default for an
unannotated name) — PEP 591 permits `x: Final = 5` with an inferred type; PyCSL's
monomorphic tag system has no inference, so the type is the opaque `Any` (sound: the
name carries the write-restriction but no type refinement, matching F3).

### 1.3 Normalization steps (in order)

1. **Recognition** — at annotation-resolution time, detect `Final[T]` / bare `Final` on
   each `arg.annotation`, `node.returns`, `AnnAssign.annotation`, and class-body field
   annotation. *Implementation site:* a new helper
   `_normalize_final_annotation(ann_expr) -> Optional[str]` invoked from
   `_m5_get_type_name` (BEFORE the Literal/Union branches) and from
   `_field_type_from_annotation_inst`. For non-Final annotations, the helper returns
   `None` and the caller proceeds with the existing logic — byte-identical for every
   unaffected driver.

2. **Inner-type resolution (F3)** — for `Final[T]`, the helper returns `τ(T)` (via
   `_m5_get_type_name_legacy` on the slice). For bare `Final`, it returns `"Any"`. F3
   (no narrowing) is satisfied *by construction*: the type tag is `T`, not a refined or
   singleton type; no narrowing VC is emitted (there is no VC at all — F3 is the absence
   of a narrowing claim).

3. **Registry collection (F1 / F2 / F2a)** — a dedicated walk
   `_collect_final_registry(module_node)` runs in `visit_Module` (after the existing
   module-level collection, before `generic_visit`) and records:
   - **F1 (module-level Final):** a top-level `AnnAssign` whose target is a `Name` and
     whose annotation is Final → `{"name", "kind": "module", "class": None,
     "allowed_writer": None}`. The declaration write (`x: Final[int] = 5`) is the ONLY
     permitted write; `allowed_writer: None` encodes "no function may write this name"
     (any write in a function body is a reassignment — F1).
   - **F2 (instance-attribute Final):** a class-body `AnnAssign` whose target is a
     `Name` (the `attr: Final[T]` declaration form, F2a — the declaration is NOT a
     write) → `{"name", "kind": "class_attr", "class": <ClassName>,
     "allowed_writer": "__init__"}`. The first and only permitted write happens in
     `__init__`.
   - **F2 (self.attr form):** a `self.attr: Final[T]` `AnnAssign` inside a class's
     `__init__` → same registry shape as the class-body form (the attribute is owned by
     the enclosing class).
   The registry is plumbed into `program_ir["final_registry"]` (an additive metadata
   key; Module 6 ignores it). It is empty for modules with no Final annotations →
   byte-identical emission (the key is omitted when empty, matching the existing
   convention for empty additive keys).

4. **No synthesis** — unlike `Literal` (which synthesizes a `requires` clause) or
   `Union` (which synthesizes a `type_decl`), `Final` synthesizes NOTHING. The
   write-policy is a semantic check (§2), not an emitted obligation. This is the
   load-bearing difference: `Final` is a *judgment about write sites*, discharged by
   inspecting the IR, not by emitting a VC.

### 1.4 Front-end files that change (on APPROVAL)

| File | Change |
|---|---|
| `src/pycsl/frontend/Module5_IREmitter.py` | add `_is_final_annotation`, `_normalize_final_annotation`, `_collect_final_registry`; call the normalizer from `_m5_get_type_name` (before Literal/Union) and `_field_type_from_annotation_inst`; call the collector from `visit_Module`; plumb `program_ir["final_registry"]` (omitted when empty). For non-Final annotations, the normalizer returns `None` and the caller falls through unchanged (byte-identical). |
| `src/pycsl/frontend/pure_ast.py` | NO change. `Final[...]` already parses to `Subscript`; bare `Final` to `Name`. |
| `src/pycsl/frontend/Module1_Ingestor.py` | NO change. `Final` is a Python annotation, not a `#@` directive. |
| `src/pycsl/frontend/import_classifier.py` | NO change. `from typing import Final` is already canonicalized to the bare head name. |

---

## 2. Static-semantics write-policy check (`src/pycsl/core_ir_semantic.py`)

### 2.1 The check

A new `_check_final(ir)` runs in `run_ir_semantic_checks` (after the per-function checks,
alongside the other module-level checks). It reuses HAPPY's *pattern* — a syntactic
write-site walk over the IR body — in its degenerate single-attribute, single-writer
form:

1. **Build the lookup** from `ir["final_registry"]`:
   - `module_finals` = `{name for entries with kind == "module"}` (F1 names).
   - `class_attr_finals` = `{name for entries with kind == "class_attr"}` (F2 attrs).
2. **Walk each function body** in `ir["functions"]` for write sites:
   - **F1 (module-level Final — write-once):** an `Assign` / `AugAssign` whose `target`
     (a bare name) is in `module_finals` → `PyCSLSemanticError`:
     `Final: cannot reassign Final name '{name}' (F1 — write-once at declaration; PEP 591)`.
     The declaration write is at module scope, which is NOT a function body, so it is
     naturally not flagged (the check sees only function-body writes — any function-body
     write to a module-level Final is by definition a reassignment).
   - **F2 (instance-attribute Final — __init__-only):** a `FieldAssign` /
     `FieldAugAssign` whose `object == "self"` and `field` is in
     `class_attr_finals` → `PyCSLSemanticError`:
     `Final: cannot write Final instance attribute 'self.{field}' outside __init__ (F2 — __init__-only writes; PEP 591)`.
     `__init__` is skipped by `_should_skip_method` (it is a dunder), so it is NEVER in
     `ir["functions"]`; therefore ANY function-body write to a Final instance attribute
     is by definition outside `__init__` → flagged. The `__init__` write itself is
     modelled via the record's `field_defaults` / `init_body` (the construction path),
     NOT as a function-body statement, so it is correctly NOT flagged.

### 2.2 Per-clause VC mapping (the load-bearing part — there are NO VCs)

Each static clause in the two-plane spec §1 maps to ONE normalization-time fact or ONE
`core_ir_semantic` check — NO VC is generated (the write-policy is decidable
syntactically, not by SMT):

| Clause | Static obligation | Mechanism |
|---|---|---|
| **F1** (module/class-level Final — write-once) | at most one write to `x`, at the declaration | `_check_final` F1 arm: any `Assign`/`AugAssign` to a module-level Final name in a function body → error. The declaration write is at module scope (not a function body) → not flagged. Two S5 cases: (a) declaration + no further writes (accept); (b) declaration + reassignment in a function (reject). |
| **F2** (instance attribute Final — __init__-only) | every write to `self.attr` is textually inside `C.__init__` | `_check_final` F2 arm: any `FieldAssign`/`FieldAugAssign` to `self.attr` (a registered class_attr Final) in a function body → error. `__init__` is never in `ir["functions"]` (dunder skip), so any function-body write is outside `__init__`. Three S5 cases: (a) write in `C.__init__` (accept — not a function-body write); (b) write in a `C` method other than `__init__` (reject); (c) write in a subclass's `__init__` (reject — see F2b note). |
| **F2a** (declaration is not a write) | `attr: Final[T]` (no `=`) is a declaration, not a write | Normalization-time: the class-body `AnnAssign` with no value records the registry entry but emits no write statement (the existing `_py_stmt_annassign` emits an `Assign` ONLY when `stmt.value is not None`). |
| **F2b** (subclass cannot widen the perimeter) | a subclass `D(C)` writing `self.attr` in `D.__init__` is still an error | **Partial:** the F2 arm catches writes in non-`__init__` methods of any class (the perimeter is owned by `C`, registered once). A subclass `D.__init__` write is caught ONLY if `D.__init__` is emitted as a function — but dunders are skipped, so `D.__init__` writes are NOT seen by the function-body walk. This is a documented **strictness gap** (gap doc §6): F2b's subclass-`__init__` case is not enforced by the IR walk. The primary F2 witness (write in a non-`__init__` method of `C`) IS enforced. A future enhancement could catch subclass-`__init__` writes in the front-end `_collect_class_fields` pass (which walks each class's own `__init__`). |
| **F3** (no narrowing) | `Final[T]` has type `T`, no refinement | Normalization-time: `_normalize_final_annotation` returns `τ(T)`, NOT a refined type. No narrowing VC is emitted (there is no VC at all). The check is the *absence* of a narrowing claim — satisfied by construction. |
| **F4** (the lowering reuses HAPPY) | the write-policy is HAPPY's no-write confinement, degenerate | Structural: `_check_final` is a syntactic write-site walk, exactly HAPPY's pattern, scoped to a single name (F1) or single `self.attr` (F2) with a single allowed writer. No new mechanism. |

### 2.3 The check seam (concrete file changes)

| File | Change |
|---|---|
| `src/pycsl/core_ir_semantic.py` | add `_check_final(ir)` (modeled on `_check_happy`'s write-site walk pattern); call it from `run_ir_semantic_checks` after the per-function loop. |
| `src/pycsl/module6_whyml/*` | **No change.** Module 6 is unchanged — no synthesized contract, no new emission path. |

---

## 3. Shim contract (runtime plane: `src/pycsl_lib/typ/__init__.py`)

Per the two-plane spec §2 (FR1–FR6) and the no-blend rule (FD2), the runtime shim
constructs the introspectable alias object and performs **NO validation**. The current
`src/pycsl_lib/typ/__init__.py` already shims `cast` (`:19`–`:21`), `Union` (`:39`–`41`),
and `Literal` (`:44`–`46`) as identities; `Final` follows the same discipline.

### 3.1 Shim surface

```python
# In src/pycsl_lib/typ/__init__.py — Final alias construction, Shimmed (FR1–FR6).

#@ ensures \result == val       # FR3: no enforcement; the alias is the value.
def Final(x0, x1, val) -> int:  # returns the typing.Final alias object
    return val                  # constructs the introspectable object (FR1, FR2)
```

(The `-> int` return tag is the existing PyCSL convention for opaque runtime objects —
the same convention `cast` / `Union` / `Literal` use. The WhyML model is `int`-typed and
the runtime object is opaque to the verifier; this is the established
Modelled-for-identity pattern. The positional `(x0, x1, val)` signature mirrors the
`Literal` / `Union` shims — the front-end's symbol-table builder resolves positional
formals, so the variadic `*args` form the spec example sketches is reduced to a fixed
positional arity for the verified surface; the runtime alias object is still constructed
by CPython's `typing.Final` at the import site.)

### 3.2 Contract discharges each FR-clause

| FR-clause | How the shim honours it |
|---|---|
| FR1 (alias object identity) | The shim returns `val` (the runtime alias object is constructed by CPython's `typing.Final` at the import site; the shim's responsibility is to NOT introduce a distinct class — FR6). |
| FR2 (introspection) | `get_origin`/`get_args` (already shimmed at `:29`–`:36`) return the alias's origin/args. **No change to those functions.** |
| FR3 (no enforcement of the write-restriction) | The shim's `#@ ensures \result == val` carries ONLY the identity postcondition. There is no `requires` on the write-policy. |
| FR4 (`isinstance` against `Final` raises) | The shim does NOT make `Final[int]` a valid `isinstance` second argument. This is a runtime property of the alias object (S4), not something the shim enforces. |
| FR5 (no validation in the shim) | The shim performs NO check on whether a write occurs. A shim that DID check would be unfaithful in exactly the way an over-strong axiom is (FD2). |
| FR6 (`Final` is not a distinct runtime class / no write-guard descriptor) | The shim does NOT introduce a distinct `Final` runtime class, a write-guard descriptor, or any runtime enforcement hook. `Final[T]` must be the `typing.Final` alias object, per FR1. Introducing a descriptor that raised on a second write would blend the planes (FD2) — REFUSED. |

### 3.3 Why the runtime shim does NOT discharge any static clause

This is the no-blend rule (FD2) made concrete: the shim's `ensures \result == val` is
SATISFIED by every value regardless of write-policy. The static clauses F1/F2/F3 are
discharged by the `core_ir_semantic._check_final` write-site walk (§2), which is
invisible to the shim. A conformance-agent authoring the S5 subset from the two-plane
spec + the shim surface alone cannot reverse-engineer the lowering — the
independence-based Gate C (c) holds.

---

## 4. Classification (`--soundness-report`)

Per the two-plane spec §4, the classification is **dual** (both planes, separately):

| Plane | Classification | Tag |
|---|---|---|
| Static | **Interpreted** | the annotation is consumed by the static plane and lowered (via the degenerate HAPPY write-policy check, §2) to a write-site obligation |
| Runtime | **Shimmed** | the runtime meaning is the introspectable `typing.Final` alias object, no enforcement (per §3) |

### 4.1 GT gap codes tagged for `Final`

**No GT gap is tagged for `Final`.** `Final` is fully sound: the write-restriction is a
syntactic write-site check — a write either is or is not textually inside the allowed
perimeter (the declaration for F1, the declaring class's `__init__` for F2) — and is
therefore decidable by construction. There is no `Any`-style gradual-consistency concern
(the write-policy does not consult the value's type), no variance, no
`ParamSpec`/`TypeVarTuple`, no polymorphic recursion, no forward-reference order beyond
what TY0 owns, no `# type: ignore`, and no runtime/static `Protocol`-style split. The
no-blend discipline (FD2 — the runtime must not "pass" the static write-restriction, and
the shim must not introduce a descriptor that enforces it) is a `Final`-local
specialization of the Literal LD2 / Union D2 no-blend rule, NOT a new GT code.

The one documented **strictness gap** (F2b subclass-`__init__` writes not caught by the
IR walk — §2.2) is a *soundness-preserving under-approximation*: it fails to reject some
programs PEP 591 rejects, but it never *accepts* a program PEP 591 rejects as a *sound*
program that PyCSL then proves something about — it merely leaves the write-policy
unchecked for that case (the write executes at runtime, which is exactly FR3's
no-enforcement). It is recorded as a gap doc (§6), not a GT code.

---

## 5. Standing gate plan (total additivity)

Per `typing-global-impl.md` §4 Gate B and the core-agent's hard rules:

### 5.1 Byte-identical emission for unaffected drivers

- The front-end normalizer (`_normalize_final_annotation`, §1.3) is a **pure function on
  the AST**: for any annotation that is NOT `Final[T]` / bare `Final`, it returns `None`
  and the caller proceeds with the existing logic unchanged. Every driver in the corpus
  that does NOT use `Final` produces byte-identical IR and byte-identical WhyML.
- The `final_registry` key is OMITTED from `program_ir` when empty (matching the existing
  convention for empty additive keys), so the serialized IR is byte-identical for
  Final-free modules.
- The corpus byte-diff gate (`bin/run-reference-tests.sh` / the standing gate) MUST
  remain green for every non-Final driver. A byte-diff on an unaffected driver is a
  regression — the normalizer is mis-recognizing a non-Final annotation.

### 5.2 `os` proof + `formal_<name>` suite re-confirmed

- The `os` library (fully green) does NOT use `Final` annotations in its verified
  surface — confirmed by `rg 'Final\[' src/pycsl_lib/os/` (zero matches in verified
  code; any match is a comment-only reference).
- The `formal_<name>` suite (json, re, warnings, …) is re-run; every previously-green
  formal test MUST remain green. A failure means the normalizer is firing on a non-Final
  annotation (the most likely regression mode) or the `_check_final` walk is
  mis-flagging a legitimate write.

### 5.3 IR-conformance corpora

- **No IR_VERSION bump.** The Final construct reuses the EXISTING `symbol_table` /
  field-type type-tag field and the EXISTING `Assign`/`FieldAssign` statement nodes. The
  `final_registry` key is an additive module-level metadata key (Module 6 ignores it),
  NOT a per-node IR field. `IR_VERSION` stays at its current value;
  `ACCEPTED_IR_VERSIONS` is unchanged. The IR-conformance corpora (core + front-end
  `*.ir.json` / `*.expected.mlw`) MUST remain green unchanged for every non-Final driver.

### 5.4 doc-coherency green

- `test-suite/annotations.md`: add the canonical entry for the `Final` annotation
  surface (§12.10, citing S2 PEP 591). Per the `pycsl-doc-coherency` skill, the entry
  must also appear in `docs/pycsl-concrete-syntax-reference.md` (§11.1 surface +
  §11.2 rejection note), `docs/pycsl-static-semantics-reference.md` (τ rule + the
  write-policy check), `docs/pycsl-translational-reference.md` (§T.14.7 translation
  table). `bin/doc-coherency.py --check` MUST remain green. (`Final` is a Python
  annotation, not a `#@` directive — doc-coherency checks `#@` directives, so the
  `Final` surface is documented in §12.10 alongside `Union`/`Optional`/`Literal`, and
  the three reference docs mirror that. The doc-coherency gate is green by construction
  for non-directive surfaces; the gate is re-run to confirm no directive-level drift was
  introduced.)

### 5.5 Non-vacuity gate

- **N/A for `Final`.** The write-policy check is a *semantic check*
  (`core_ir_semantic._check_final`), NOT a VC. `--check-vacuity` operates on Why3 goals;
  no new goal is emitted for `Final` (F3 is the absence of a narrowing claim — there is
  no VC to be vacuous). The non-vacuity gate is re-run on the witness driver (§5.6) to
  confirm NO new vacuous VC was accidentally introduced (e.g. by the inner-type
  resolution perturbing an existing clause). A false-twin on the witness's postcondition
  MUST still FAIL (the witness's `\result == x` postcondition is non-vacuous).

### 5.6 Witness / negative drivers (the coordinator's gate items 5–7)

| Gate item | Driver | Expected |
|---|---|---|
| 5 (F1 witness) | `x: Final[int] = 5` at module scope; `def f() -> int: return x` | VCs discharge (SUCCESS) — the declaration write is at module scope (not a function body); `f` reads `x` (a read, not a write); `_check_final` sees no write site → no error. |
| 5 (F1 negative) | as above, but `def f(): x = 10` (reassignment in a function) | `_check_final` F1 arm → `PyCSLSemanticError: Final: cannot reassign Final name 'x' ...` (exit 1) |
| 6 (F2 witness) | `class C: attr: Final[int]; def __init__(self): self.attr = 0` (and a reader) | VCs discharge (SUCCESS) — the `__init__` write is in the construction path (not a function body); no other method writes `self.attr` → no error. |
| 6 (F2 negative) | as above, plus `def m(self): self.attr = 1` | `_check_final` F2 arm → `PyCSLSemanticError: Final: cannot write Final instance attribute 'self.attr' outside __init__ ...` (exit 1) |
| 7 (runtime shim) | `Final(int, 5)` identity | the shim's `ensures \result == val` discharges (SUCCESS) — the runtime does NOT enforce the write-restriction (FR3) |

---

## 6. Gap docs

- **F2b (subclass `__init__` writes) — strictness gap.** The F2 arm of `_check_final`
  walks `ir["functions"]` for `FieldAssign`/`FieldAugAssign` to `self.attr`. Because
  `__init__` is a dunder (skipped by `_should_skip_method`), a subclass `D(C)`'s
  `__init__` write to `self.attr` is NOT in `ir["functions"]` and is therefore NOT
  flagged. PEP 591 (F2b) rejects this; PyCSL does not. This is a
  **soundness-preserving under-approximation**: PyCSL fails to reject a program PEP 591
  rejects, but it does not prove anything unsound about it — the write executes at
  runtime (FR3 no-enforcement), and no static claim depends on the write-policy being
  enforced for that case. A future enhancement could catch subclass-`__init__` writes in
  the front-end `_collect_class_fields` pass (which walks each class's own `__init__`)
  by cross-referencing the base-class Final registry. Recorded as a gap doc, NOT a GT
  code (no unsoundness; just a missed diagnostic).

---

## 7. Deliverable checklist (on APPROVAL)

- [x] Front-end: `_is_final_annotation`, `_normalize_final_annotation`,
      `_collect_final_registry` in `Module5_IREmitter.py`; normalizer wired into
      `_m5_get_type_name` and `_field_type_from_annotation_inst`; collector wired into
      `visit_Module`; `program_ir["final_registry"]` plumbed (omitted when empty).
- [x] Module 6: NO change (no synthesized contract; the inner type flows through the
      existing type-tag resolution).
- [x] `core_ir_semantic.py`: `_check_final(ir)` (F1 + F2 arms), wired into
      `run_ir_semantic_checks`.
- [x] `src/pycsl_lib/typ/__init__.py`: `Final(*args, val)` shim (identity
      `ensures \result == val`, NO descriptor).
- [x] `test-suite/annotations.md` (§12.10) + three reference docs; doc-coherency green.
- [x] `--soundness-report`: `Final` classified Interpreted (static) / Shimmed (runtime);
      NO GT gap tag; the F2b strictness gap recorded as a gap doc (§6).
- [x] Standing gate: corpus byte-diff green for all non-Final drivers (byte-identical);
      `os` proof + `formal_os_pure` re-confirmed; NO IR_VERSION bump; `--check-vacuity`
      green (no new vacuous VC); F1 witness SUCCESS, F1 negative ERROR; F2 witness
      SUCCESS, F2 negative ERROR; runtime shim identity discharges.
- [x] NO conformance-suite or shim-faithfulness-driver edits (the conformance-agent
      authors those, never the core-agent).

---

## 8. Open questions for the coordinator (editorial)

1. **F2b enforcement.** This DRAFT implements F2b partially (non-`__init__` method
   writes of any class are caught; subclass-`__init__` writes are not, because dunders
   are skipped from `ir["functions"]`). The two-plane spec §1.2 F2b names one S5 case
   (write to `self.attr` in `D.__init__` where `D(C)` — reject). (Recommendation: ship
   the partial enforcement now with the §6 gap doc; add front-end subclass-`__init__`
   detection in a follow-up if the conformance-agent's F2b case is load-bearing.)
2. **`Final` on a parameter.** This DRAFT resolves `def f(x: Final[int])` to type `int`
   (F3) but does NOT register `x` in the final registry (parameters are not
   module/class-level names). PEP 591 treats a Final parameter as write-once in the body.
   (Recommendation: defer — the spec's two witnesses are F1 module-level and F2 instance
   attribute; a parameter-Final check is a future enhancement, not a soundness gap.)
3. **Bare `Final` (no type argument).** This DRAFT resolves `x: Final = 5` to type
   `Any` (no inference). PEP 591 permits inferred-type `Final`. (Recommendation: `Any`
   is sound — the name carries the write-restriction but no type refinement; defer
   inference.)
