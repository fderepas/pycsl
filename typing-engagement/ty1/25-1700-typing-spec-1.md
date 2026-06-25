# 25-1700-typing-spec-1.md — `Union` Implementation Spec (DRAFT)

**Status:** DONE (core-agent implemented both planes; standing gate green).
**Tier:** TY1 (monomorphic refinements).
**Construct:** `Union` (PEP 484 `Union[X, Y]` + PEP 604 `X | Y`).
**Two-plane spec authority:** `typing-engagement/ty1/union-twoplane-spec.md` (APPROVED).
**Global guides honoured:** `typing-global-impl.md` §4 (per-construct pipeline + gates) and §5
(TY1 obligations, incl. NoReturn × vacuity); `docs/typing-global-overview.md` §4.2 (TY1
lowering locus = Module 6 lowering table + injected obligations).
**Sound expressibility reminder (overview §2.1):** the IR/WhyML lower bound may be STRICTER
than S1, never weaker. Where the type system is deliberately unsound (`Any`), PyCSL refuses
to import the unsoundness (GT1).
**No-blend reminder (overview §2.3 / D4):** the static-plane obligations (§1 of the two-plane
spec) and the runtime-plane identity/introspection behaviour (§2 of the two-plane spec) are
carried as SEPARATE contracts. The runtime shim must not be allowed to discharge a static
narrowing clause.

**This is a planning document. No `src/pycsl/` file is modified by this DRAFT.** On
coordinator APPROVAL, the core-agent implements both planes and runs the standing gate.

---

## 0. Design summary (one paragraph)

`Union[A, B, ...]` (and the PEP 604 spelling `A | B | ...`) is **desugared at the
front-end normalization seam** into a per-annotation-site synthesized `#@ datatype`
variant declaration of the shape `type _union_N = Arm_0 of T_0 | Arm_1 of T_1 | …`, plus
an injection wrapper per arm. This reuses PyCSL's **existing** sum-type machinery (the
`_variant_types` map, the `type_decl` IR node, the Why3 `type t = …` emission in
`module6_whyml/preamble.py`, and the constructor-pattern match lowering in
`stmt_control_flow.py`) — **no new IR node is introduced, no IR_VERSION bump is
required.** The runtime plane is a thin shim in `src/pycsl_lib/typ/__init__.py` that
constructs the introspectable `typing.Union` alias / `types.UnionType` object and
performs NO validation (R1–R8).

---

## 1. Normalization rule (front-end: `src/pycsl/frontend/`)

### 1.1 Surface forms to recognize

Per the two-plane spec §1.0 (C1, C1a–C1c), TWO surface spellings denote the same static
type and must be normalized to ONE canonical IR form:

| Surface | AST shape (post-`pure_ast`) | Canonical spelling |
|---|---|---|
| `Union[X, Y]` | `Subscript(value=Name(id="Union"), slice=Tuple([X, Y]) \| X)` | `union` |
| `Union[X]` (degenerate, C1c) | `Subscript(value=Name(id="Union"), slice=X)` | `union` (one arm) |
| `X \| Y` (PEP 604) | `BinOp(left=X, op=BitOr, right=Y)` (left-assoc; nests as `BinOp(BinOp(X,BitOr,Y),BitOr,Z)`) | `union` |
| `Optional[X]` (C1b) | `Subscript(value=Name(id="Optional"), slice=X)` | `union` with `None` arm |

`typing.Union` and `typing.Optional` are recognized by the bare head name (the
import-rewriting in `import_classifier.py` already canonicalizes `from typing import
Union`/`Optional`). PEP 604 `X | Y` is recognized structurally at the BinOp level — note
`pure_ast.py:529` already parses `|` as `BitOr` and `pure_ast.py:3256` unparses it.

### 1.2 Canonical IR annotation form

The canonical IR annotation form is a **synthesized datatype**, registered in the
function/class `symbol_table` under a fresh variant name:

```
symbol_table[var] = "_union_<scope>_<idx>"      # names the synthesized variant type
# plus a per-site type_decl of kind "variant":
#   { "kind": "variant",
#     "name": "_union_<scope>_<idx>",
#     "variants": [ {"ctor": "Arm_0", "fields": [("v", T_0)]}, ... ] }
```

The arm type tags `T_i` are the existing IR type tags (`int`, `str`, `bool`, `bytes`,
`float`, `list`, record/variant names). `None` is its own arm (a nullary constructor
`Arm_None`), which makes C5 (`is None` narrowing) lower to a constructor-pattern match
arm — exactly the seam the two-plane spec §1.4 names.

### 1.3 Normalization steps (in order)

1. **Recognition** — at annotation-resolution time, walk each `arg.annotation`,
   `node.returns`, and `AnnAssign.annotation`; detect the four surface forms above.
   *Implementation site:* a new helper `_normalize_union_annotation(ann_expr)` invoked
   from `_m5_get_type_name` (`Module5_IREmitter.py:1607`) and
   `_field_type_from_annotation` (`Module5_IREmitter.py:1327`) BEFORE the existing
   parametric-annotation branches. This keeps every unaffected driver byte-identical:
   annotations that are NOT `Union`/`|`/`Optional` skip the helper entirely.

2. **Idempotence / ordering / degenerate (C1a, C1c)** — the helper applies:
   - de-duplicate arms by structural equality of the arm type tag (so `Union[A, A]` →
     one arm, identical to `A`);
   - order arms by a stable canonical order (source order, with `None` placed last
     when present, matching CPython `Lib/typing.py`'s `_UnionGenericAlias` rendering
     for `Optional[X]`); the order is a *rendering* detail only — the static judgments
     C2/C3 are order-independent.

3. **`Any` refusal (C4 / GT1 / D3)** — if any arm normalizes to the `Any` tag, the
   helper records the occurrence for `--soundness-report` (GT1 tag) and **drops the
   arm from the synthesized variant** (the static plane discharges C2/C3 against the
   non-`Any` arms only). It does NOT make the Union a universal sink. The runtime
   shim is unaffected — R1–R8 still construct the full `Union[Any, ...]` object.

4. **Synthesis** — for each unique Union annotation site, emit ONE `type_decl`
   (variant) into the module's `type_decls` list (the existing field on the IR
   module, consumed by `preamble.py` for Why3 `type t = …` emission). The variant
   name is deterministic and scope-mangled (`_union_<func>_<idx>`) so the same source
   always produces the same IR.

5. **Tag the annotation** — the symbol-table entry for the variable / parameter /
   return is set to the synthesized variant name, so `_param_type_str`
   (`functions.py:13`) and `_compute_return_type` (`functions.py:514`) emit the
   variant type via the EXISTING `if symtype in self._variant_types:` branches
   (`functions.py:49` and `:536`). No new branch in those functions is required.

### 1.4 Front-end files that change (on APPROVAL)

| File | Change |
|---|---|
| `src/pycsl/frontend/Module5_IREmitter.py` | add `_normalize_union_annotation` helper; call it from `_m5_get_type_name` (`:1607`), `_field_type_from_annotation` (`:1327`), and the return-annotation path (`:1757`–`:1801`); append synthesized `type_decl`s to the module IR. |
| `src/pycsl/frontend/pure_ast.py` | NO change. PEP 604 `X \| Y` already parses to `BinOp(BitOr)` (`:529`, `:3256`); `Union[...]` already parses to `Subscript`. The normalization runs on the AST, not the grammar. |
| `src/pycsl/frontend/Module1_Ingestor.py` | extend the `_MODULE_PREFIXES` recognition only if a `#@ union` directive surface is added (NOT in this DRAFT — Union is a Python annotation, not a `#@` directive). **Likely no change.** |
| `src/pycsl/frontend/import_classifier.py` | confirm `from typing import Union, Optional` is canonicalized to the bare head name (already is). **Likely no change.** |

---

## 2. Lowering table entry (Module 6: `src/pycsl/module6_whyml/`)

### 2.1 The lowering

The canonical Union annotation lowers to a **Why3 sum type with one constructor per
arm** (the two-plane spec §1.4 names this exact mechanism as dischargeable):

```whyml
type _union_<scope>_<idx> =
  | Arm_0 of <T_0_whyml>
  | Arm_1 of <T_1_whyml>
  | Arm_None          (* only when the Union includes None *)
```

where each `<T_i_whyml>` is the WhyML type produced by the existing
`_param_type_str` resolver for that arm's tag. This emission goes through the
EXISTING variant-type path in `module6_whyml/preamble.py` (the `_variant_types` map
populated from `type_decls` of kind `variant`) — there is already a `type t = A | B`
emission seam, used today by user `#@ datatype` declarations.

### 2.2 Per-clause VC mapping (the load-bearing part)

Each static clause in the two-plane spec §1 maps to ONE VC, generated by reusing
existing Module 6 mechanisms — no new VC kind:

| Clause | Static obligation | VC / mechanism |
|---|---|---|
| **C2** (arm membership) | `v: T` assignable to `Union[A_i]` iff some `A_i` accepts `T` | Per-arm injection goal: `goal union_N__arm_i_assignable : forall v: T. <T ⊑ A_i>` — emitted by a new `_emit_union_arm_vc` helper that mirrors `_emit_narrowing_vc` (`functions.py:354`). The injection `Arm_i(v)` is well-typed iff `T ⊑ A_i`; Why3 type-checking discharges it. A flow where NO arm accepts `T` fails to type-check → static rejection (one S5 accept case per arm, one reject case for an unassignable `T`). |
| **C3** (reverse flow) | `Union[A_i]` assignable to `T` iff EVERY `A_i ⊑ T` | Per-arm extraction goal: `goal union_N__arm_i_projects_to_T : forall v: _union_N. (\is_ctor(v, Arm_i)) -> <A_i ⊑ T>`. Each arm must project (via `\payload`) to `T`; a failing arm is a static rejection. |
| **C5** (`is None` narrowing) | `if x is None:` on `x: Union[A, None]` → True-branch `x: None`, False-branch `x: A` (or `Union[…]` minus None) | Lowered to a `match x with Arm_None -> <true-branch> | _ -> <false-branch>` via the EXISTING constructor-pattern match lowering in `stmt_control_flow.py:562`. The path-condition VC is the standard match-exhaustiveness goal. The `None` arm is the `Arm_None` constructor; the False-branch is the wildcard. |
| **C6** (`isinstance` narrowing) | `if isinstance(x, C):` on `x: Union[A_i]` → True-branch sub-union of arms assignable to `C`, False-branch the rest | Lowered to a match with a per-arm guard `is_instance_of(\payload(v, Arm_i), C)` — the guard becomes a path condition. If NO arm is assignable to `C`, the True-branch match is exhaustive over the empty set → a **dead-branch VC** (Why3 sees the True-branch as unreachable, `goal union_N__dead_branch_isinstance_C`). |
| **C7** (`TypeIs`/`TypeGuard`) | `g(x) -> TypeIs[T]` narrows `x: Union[…]` to `T` on True, `Union[…] \ T` on False | Reuses the existing TypeIs-constructor correspondence (overview §4.2: "a `TypeIs` function's boolean result carries a constructor fact"). The guard's `ensures \result == True ⟹ <shape>` contract supplies the narrowing predicate. **Detailed mechanism belongs to the PEP 742 construct's spec, not this one — flagged for cross-reference at implementation time.** |
| **C8** (no narrowing without a guard) | truthiness / attribute access does NOT refine | No VC is emitted for those constructs; the variable retains its `Union` variant type. The static rejection (an S5 case claiming narrowing where none is licensed) is a `core_ir_semantic` well-formedness check: a path condition not derived from `is None` / `isinstance` / `TypeIs` / `TypeGuard` may not refine the variant. |
| **C9** (match exhaustiveness) | a `match` on `Union[A_i]` must cover every arm | Why3's native match-exhaustiveness check (the constructor-pattern match in `stmt_control_flow.py:562` already produces this). A non-exhaustive match is a Why3 type error → static rejection. |
| **C10** (post-match assignability) | after exhaustive match, arm-bound `y: A_i` is assignable to any `T` with `A_i ⊑ T` | Discharged by the same per-arm extraction goal as C3, in the arm's match branch. |
| **C11** (unreachable arm) | a case pattern accepting values no arm can produce is dead | A Why3 match with a case whose pattern is subsumed by an earlier arm is flagged by Why3's redundancy check (or, where Why3 is silent, by a `core_ir_semantic` post-pass). |

### 2.3 The lowering seam (concrete file changes)

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/preamble.py` | **No new path.** Confirm the existing variant-type emission (around `:2530` / `:2727`–`:2765`) handles synthesized `_union_*` names. It already does — that path is driven by `type_decls` of kind `variant`, which is exactly what the front-end synthesizes (§1.2). |
| `src/pycsl/module6_whyml/functions.py` | add `_emit_union_arm_vc(name, union_variant, arms)` modeled on `_emit_narrowing_vc` (`:354`); call it from the function-emission path that already emits narrowing VCs (`:705`). The existing `_param_type_str` (`:13`, branch at `:49`) and `_compute_return_type` (`:514`, branch at `:536`) need **no change** — they already resolve `_variant_types` entries. |
| `src/pycsl/module6_whyml/stmt_control_flow.py` | **No new path.** The existing constructor-pattern match lowering (`:562`) handles `Arm_*` patterns. Confirm `is None` lowering routes through it (it should, since `None` is now a nullary constructor). |
| `src/pycsl/module6_whyml/expressions.py` | **No new path.** The existing applied-constructor path (`:1436`) and nullary-constructor-as-value path (`:2375`) handle `Arm_i(v)` and `Arm_None`. |
| `src/pycsl/core_ir_semantic.py` | add the C8 well-formedness check (a path condition not derived from a recognized guard may not refine a Union-typed variable) and the C11 dead-arm reporting. Both are *static-semantics* checks, not lowering. |

---

## 3. Shim contract (runtime plane: `src/pycsl_lib/typ/__init__.py`)

Per the two-plane spec §2 (R1–R8) and the no-blend rule (D4), the runtime shim constructs
the introspectable object and performs **NO validation**. The current
`src/pycsl_lib/typ/__init__.py` already shims `cast` as an identity (`:5`–`:7`); `Union`
follows the same discipline.

### 3.1 Shim surface

```python
# In src/pycsl_lib/typ/__init__.py — Union alias construction, Shimmed (R1–R8).

#@ ensures \result == val       # R3: no enforcement; the alias is the value.
def Union(*args) -> int:         # returns the typing.Union alias object
    return _typing_Union(args)   # constructs the introspectable object (R1, R2)
```

(The `-> int` return tag is the existing PyCSL convention for opaque runtime objects —
the same convention `cast` uses. The WhyML model is `int`-typed and the runtime object
is opaque to the verifier; this is the established Modelled-for-identity pattern.)

### 3.2 Contract discharges each R-clause

| R-clause | How the shim honours it |
|---|---|
| R1 (object identity) | The shim returns the `typing.Union` alias object (constructed via the stdlib `_typing_Union` helper, exposed by the import-rewriting in `import_classifier.py`). `Union[X, X]` collapses to `X` because the stdlib does. |
| R2 (introspection) | `get_origin`/`get_args` (already shimmed at `:11`–`:23`) return the alias's origin/args. **No change to those functions** — they already return introspection-only values. |
| R3 (no enforcement) | The shim's `#@ ensures \result == val` carries ONLY the identity postcondition. There is no `requires` on the arm types. |
| R4 (`isinstance` against `Union` raises) | The shim does NOT make `Union[X, Y]` a valid `isinstance` second argument. This is a runtime property of the alias object, not something the shim enforces — the alias object raises `TypeError` natively (S4). |
| R5 (PEP 604 `X \| Y` is `types.UnionType`) | `X \| Y` is a BinOp at the AST level; the runtime evaluation produces a `types.UnionType` object. The shim does NOT intercept this — PEP 604 `X \| Y` is not a function call, it is an operator. The shim's responsibility is limited to the `Union[...]` spelling. |
| R6 (`isinstance(v, X \| Y)` permitted) | Same as R5 — runtime behaviour of `isinstance` against a `types.UnionType` is native to CPython; the shim does not touch it. |
| R7 (no annotation enforcement) | The shim's contract is identity only — it cannot enforce the annotation even if it wanted to (there is no `requires` clause on the arm types). |
| R8 (no validation in the shim) | The shim performs NO check on whether `val` belongs to any arm. A shim that DID check would be unfaithful in exactly the way an over-strong axiom is (D4). |

### 3.3 Why the runtime shim does NOT discharge any static clause

This is the no-blend rule (D4) made concrete: the shim's `ensures \result == val` is
SATISFIED by every value regardless of type. The static clauses C2–C11 are discharged by
the Why3 sum-type VCs (§2.2), which are invisible to the shim. A conformance-agent
authoring the S5 subset from the two-plane spec + the shim surface alone cannot
reverse-engineer the lowering — the independence-based Gate C (c) holds.

---

## 4. Classification (`--soundness-report`)

Per the two-plane spec §4, the classification is **dual** (both planes, separately):

| Plane | Classification | Tag |
|---|---|---|
| Static | **Interpreted** | the annotation is consumed by the static plane and lowered to obligations (per §2.2) |
| Runtime | **Shimmed** | the runtime meaning is the introspectable object, no enforcement (per §3) |

### 4.1 GT gap codes tagged for `Union`

- **GT1** — `Any` in a Union arm. Per C4 / D3, the static plane refuses `Any` as a
  Union arm (opaque, operation-barren, dropped from the synthesized variant, reported
  every occurrence). **Permanent, by design** (overview §5).
- **GT7** (analogous, NOT a new code) — D2 documents the `isinstance` asymmetry: the
  static C6 narrowing must NOT be discharged by the runtime `isinstance(v, X | Y)`
  membership check. This is a Union-local restatement of the no-blend rule, tagged in
  the report as a `no_blend_isinstance_union` note, not a new GT code.
- **GT8** — the S5 conformance subset for `Union` is the conformance-agent's standing
  artifact (NOT this DRAFT's deliverable). Each clause C1–C11 above names the S5 case
  shape it commits to.

No other GT gap is tagged for `Union` at TY1.

---

## 5. Standing gate plan (total additivity)

Per `typing-global-impl.md` §4 Gate B and the core-agent's hard rules:

### 5.1 Byte-identical emission for unaffected drivers

- The front-end normalization helper (`_normalize_union_annotation`,
  §1.3) is a **pure function on the AST**: for any annotation that is NOT one of the
  four Union surface forms, it returns the existing IR tag unchanged. Every driver in
  the corpus that does NOT use `Union`/`|`/`Optional` produces byte-identical IR and
  byte-identical WhyML.
- The corpus byte-diff gate (`bin/run-reference-tests.sh` / the standing gate) MUST
  remain green for every non-Union driver. A byte-diff on an unaffected driver is a
  regression — the helper is mis-recognizing a non-Union annotation.

### 5.2 `os` proof + `formal_<name>` suite re-confirmed

- The `os` library (now fully green, down to 1 `\trusted` line) does NOT use `Union`
  annotations in its verified surface — confirm by `rg 'Union\[' src/pycsl_lib/os/`
  before claiming additivity. (Expected: zero matches in verified code; any match is
  a comment-only reference.)
- The `formal_<name>` suite (json, re, warnings, …) is re-run; every previously-green
  formal test MUST remain green. A failure means the normalization helper is firing on
  a non-Union annotation (the most likely regression mode).

### 5.3 IR-conformance corpora

- **No IR_VERSION bump.** The Union construct reuses the EXISTING `type_decl` (variant)
  IR node and the EXISTING `symbol_table` field. No new IR field is introduced.
  `IR_VERSION` stays at `1.2`; `ACCEPTED_IR_VERSIONS` stays `{"1.0", "1.1", "1.2"}`.
  The IR-conformance corpora (core + front-end `*.ir.json` / `*.expected.mlw`) MUST
  remain green unchanged for every non-Union driver.
- **If** (contingency) the coordinator judges that the synthesized `_union_*` variant
  name needs to be stable across runs for golden-comparison purposes, the
  name-mangling scheme (`_union_<func>_<idx>`) is documented in `docs/ir.md` §10 as a
  non-versioned rendering detail — STILL no IR_VERSION bump, because the schema is
  unchanged.

### 5.4 doc-coherency green

- `test-suite/annotations.md`: add the canonical entry for the `Union` annotation
  surface (citing S2 PEP 484 / PEP 604). Per `pycsl-doc-coherency` skill, the entry
  must also appear in `docs/pycsl-concrete-syntax-reference.md`,
  `docs/pycsl-static-semantics-reference.md`, `docs/pycsl-translational-reference.md`,
  and a `config/skills/` skill (likely `pycsl-annotate`). `bin/doc-coherency.py
  --check` MUST remain green.

### 5.5 Non-vacuity gate (NOT vacuous here, see §6)

- Every new VC in §2.2 (per-arm assignability, per-arm projection, dead-branch
  isinstance) MUST pass `--check-vacuity`, and a false-twin (an impossible
  postcondition injected via `bin/false-twin.py`) on each MUST FAIL. The per-arm
  injection goal `union_N__arm_i_assignable` is non-vacuous because the arm type
  `A_i` is a real IR type tag (not `Any` — GT1 drops `Any` arms before VC emission,
  so no vacuous `forall v: Any. ...` goal is ever generated).

---

## 6. NoReturn × vacuity gate

**N/A for `Union`.** The NoReturn × vacuity interaction (the sharpest TY1 obligation,
`typing-global-impl.md` §5 item 2) is owned by the **`NoReturn` construct's spec**, not
this one. A `NoReturn`-typed function carries a `false` postcondition by design; the
vacuity gate must exempt declared-`NoReturn` functions or it flags them as vacuous.

`Union` does NOT interact with the vacuity gate in the NoReturn-specific way:
- A `Union[..., NoReturn]` annotation is NOT a `NoReturn` return type — it is a Union
  whose one arm is the `NoReturn` type. The arm is treated as a divergent arm: a value
  of `Union[A, NoReturn]` on the `NoReturn` arm never returns. The synthesized
  variant's `Arm_NoReturn` constructor is emitted but unreachable in any well-typed
  body (a function that returns a `Union[A, NoReturn]` value never constructs the
  `NoReturn` arm — to do so it would have to diverge). This is a **dead-constructor**
  property, flagged in `core_ir_semantic` as a warning (NOT a vacuity failure).
- **Cross-reference flag:** if a function's RETURN type is `Union[..., NoReturn]` AND
  the function is itself declared `NoReturn`, the two planes interact — the
  `NoReturn` spec's vacuity-gate exemption must apply. This edge case is noted here
  for the `NoReturn` spec to handle; `Union`'s responsibility is only to emit the
  dead-constructor warning.

---

## 7. Deliverable checklist (on APPROVAL)

- [x] Front-end: `_normalize_union_annotation` in `Module5_IREmitter.py`; wired into
      `_m5_get_type_name`, `_field_type_from_annotation`, and the return-annotation path.
- [x] Module 6: `_emit_union_arm_vc` in `functions.py` (modeled on `_emit_narrowing_vc`);
      confirmed the existing variant-emission/match-lowering paths handle `_union_*`.
      Added `_try_union_is_none_match` in `stmt_control_flow.py` for C5 `is None` lowering
      (Why3 forbids `=` on algebraic types in a program `if`). Added return-value
      auto-injection in `_handle_return_stmt` (§0 injection wrapper per arm).
- [x] `core_ir_semantic.py`: C8 well-formedness check + C11 dead-arm reporting + GT1
      `Any`-arm reporting.
- [x] `src/pycsl_lib/typ/__init__.py`: `Union` shim (identity `ensures \result == val`).
- [x] `test-suite/annotations.md` + three reference docs; doc-coherency green.
- [x] `--soundness-report`: `Union` classified Interpreted (static) / Shimmed (runtime),
      GT1 tag emitted.
- [x] Standing gate: corpus byte-diff green for non-Union drivers (683/686, the 3
      confirmed failures are pre-existing 0700/0701/0714, unrelated to Union); `os`
      proof + formal suite re-confirmed; NO IR_VERSION bump; `--check-vacuity` green
      on every new VC; false-twin green on every new VC.
- [x] NO conformance-suite or shim-faithfulness-driver edits (the conformance-agent
      authors those, never the core-agent). The two updated reference-corpus drivers
      (0349/0350) are PyCSL's own tests, not the typing conformance suite — they
      encoded the OLD Optional/Union collapse-to-int behavior and were updated to
      exercise the new variant seam.

---

## 8. Open questions for the coordinator (editorial)

1. **`Optional[X]` reuse.** This DRAFT treats `Optional[X]` as `Union[X, None]` (per
   C1b), sharing the Union machinery. The `Optional` construct has its own two-plane
   spec (separate TY1 construct); confirm the coordinator wants the SAME lowering
   seam, or a dedicated `Optional` path. (Recommendation: same seam — `Optional` IS
   `Union[X, None]` per S1.)
2. **Variant name stability.** Is the deterministic name-mangling
   (`_union_<func>_<idx>`) acceptable for the IR-conformance goldens, or should the
   name be content-hashed (`_union_<hash_of_arm_types>`) so two sites with the same
   arm types share a variant? (Recommendation: per-site names for now; revisit if
   VC volume becomes a concern at TY2/TY3.)
3. **C7 (TypeIs/TypeGuard) scope.** This DRAFT flags C7 as cross-referenced to the
   PEP 742 construct's spec. Confirm the coordinator accepts that `Union`'s
   responsibility for C7 is limited to "the variant type is matchable" and the
   TypeIs-constructor correspondence is owned elsewhere.
