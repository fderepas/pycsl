# 26-0000-typing-spec-2.md — `Literal` Implementation Spec

**Status:** DONE (core-agent implemented both planes; standing gate green).
**Tier:** TY1 (monomorphic refinements).
**Construct:** `Literal` (PEP 586 `Literal[v1, ..., vn]`).
**Two-plane spec authority:** `typing-engagement/ty1/literal-twoplane-spec.md` (APPROVED).
**Global guides honoured:** `typing-global-impl.md` §4 (per-construct pipeline + gates) and §5
(TY1 obligations, incl. NoReturn × vacuity); `docs/typing-global-overview.md` §4.2 (TY1
lowering locus = Module 6 lowering table + injected obligations).
**Sound expressibility reminder (overview §2.1):** the IR/WhyML lower bound may be STRICTER
than S1, never weaker. `Literal` is fully sound — finite enumeration — so NO GT gap is
tagged for it (two-plane spec §4).
**No-blend reminder (overview §2.3 / LD3):** the static-plane obligations (§1 of the
two-plane spec) and the runtime-plane identity/introspection behaviour (§2 of the
two-plane spec) are carried as SEPARATE contracts. The runtime shim must not be allowed
to discharge a static narrowing clause.

**This is a planning document. No `src/pycsl/` file is modified by this DRAFT.** On
coordinator APPROVAL, the core-agent implements both planes and runs the standing gate.

---

## 0. Design summary (one paragraph)

`Literal[v1, ..., vn]` is **desugared at the front-end normalization seam** into a
per-annotation-site synthesized **ground `requires` clause** of the shape
`requires { x = v1 \/ x = v2 \/ ... \/ x = vn }`, where each `v_i` is a concrete
literal value (int/str/bool/None per L4). This reuses PyCSL's **existing** `requires`
mechanism end-to-end (the `contracts.requires` IR list, the `requires { ... }` emission
in `module6_whyml/functions.py:274`, and the existing BinOp/Number/String/Bool/None IR
expression nodes consumed by `_expr_to_whyml`). **NO new IR node is introduced, NO
IR_VERSION bump is required, NO new VC kind is introduced.** The parameter's WhyML type
stays the literal's base type (`int` for `Literal[1, 2]`, `string` for `Literal["a","b"]`,
`int` for `Literal[True]`, `int` for `Literal[None]`), so a `Literal[1, 2]`-typed
parameter is emitted as `let f (x: int) requires { x = 1 \/ x = 2 } = ...` — exactly the
shape the coordinator's witness driver (gate item 5) checks for. The runtime plane is a
thin shim in `src/pycsl_lib/typ/__init__.py` that constructs the introspectable
`typing.Literal` alias object and performs NO validation (LR1–LR8).

### 0.1 Why ground requires (and not a sum-type variant)

`Union`/`Optional` (25-1700-typing-spec-1) lower to a synthesized variant because their
arms are *types*, so the natural WhyML model is an algebraic type with one constructor
per arm. `Literal`'s arms are *values*, not types: `Literal[1, 2]` enumerates the two
int values 1 and 2. The natural WhyML model is therefore a value-set predicate (a
precondition), NOT a type — there is no constructor to inject into. The ground-requires
disjunction `x = 1 \/ x = 2` is exactly that predicate, and it is SMT-cheap (finite
disjunction of concrete-value equalities, decidable by construction — two-plane spec §1.6).
This is the divergence the spec-agent named (LD1: "ground requires vs introspectable
alias object"): the static plane is a precondition, the runtime plane is an alias object.

### 0.2 What is NOT introduced

- **No new IR node.** `Literal` reuses the existing `BinOp` (`op: "or"`), `==` BinOp,
  `Var`, `Number`, `String`, `Bool`, `None` IR expression nodes — exactly the nodes
  `_csl_to_ir` already produces for a hand-written `#@ requires x == 1 or x == 2`
  clause. The synthesized `requires` clause is a list of such IR expression dicts
  appended to `func_ir["contracts"]["requires"]`.
- **No IR_VERSION bump.** The IR schema is unchanged. `IR_VERSION` stays at its current
  value; `ACCEPTED_IR_VERSIONS` is unchanged. The IR-conformance corpora (core +
  front-end `*.ir.json` / `*.expected.mlw`) MUST remain green unchanged for every
  non-Literal driver.
- **No new VC kind.** The synthesized `requires` becomes a standard Why3 precondition
  goal, exactly as a hand-written `#@ requires` would. No `_emit_*_vc` helper is added.
- **No new `core_ir_semantic` check beyond L4a (bytes rejection).** L5 (order
  independence) / L5a (dedup) / L5b (degenerate) are handled at normalization time (the
  helper canonicalizes the value list); L3 (exhaustiveness) and L2 (narrowing) are
  emergent: L2 narrows via the standard path-condition VC on the existing `if x == v`
  lowering (no new node — the disjunction is in the precondition, the path condition is
  the runtime `==` test, and Why3's standard precondition-preservation-on-branch handles
  the refinement); L3 is the existing match/if-chain exhaustiveness discipline (a
  non-exhaustive chain without a catch-all fails to discharge the postcondition when the
  residual value set is non-empty — covered by the standing VCs, not a new check).

---

## 1. Normalization rule (front-end: `src/pycsl/frontend/Module5_IREmitter.py`)

### 1.1 Surface form to recognize

Per the two-plane spec §1.1 (L1) and §1.4 (L4, L4a, L4b), ONE surface form denotes the
`Literal` static type:

| Surface | AST shape (post-`pure_ast`) | Canonical spelling |
|---|---|---|
| `Literal[v1, ..., vn]` | `Subscript(value=Name(id="Literal"), slice=Tuple([v1, ..., vn]) \| v1)` | `literal` |
| `Literal[v]` (degenerate, L5b) | `Subscript(value=Name(id="Literal"), slice=v)` | `literal` (one value) |

`typing.Literal` is recognized by the bare head name (the import-rewriting in
`import_classifier.py` already canonicalizes `from typing import Literal`). PEP 586
forbids nested `Literal` (`Literal[Literal[1, 2]]` — L5c); a nested form is a static
error (L5c). No PEP 604 spelling exists for `Literal` (it has no `|` form).

### 1.2 Canonical IR annotation form

The canonical IR form is the parameter's **base type tag** (the literal's Python type —
`int` for `Literal[1, 2]` / `Literal[True]` / `Literal[None]`; `str` for
`Literal["a", "b"]`), PLUS a synthesized `requires` clause appended to the function's
`contracts.requires` list:

```
# For `def f(x: Literal[1, 2]) -> int`:
#   symbol_table["x"] = "int"     # the base type tag (unchanged from a bare `int` param)
#   contracts.requires.append({
#       "type": "BinOp", "op": "or",
#       "left":  {"type": "BinOp", "op": "==",
#                 "left":  {"type": "Var", "name": "x"},
#                 "right": {"type": "Number", "value": 1}},
#       "right": {"type": "BinOp", "op": "==",
#                 "left":  {"type": "Var", "name": "x"},
#                 "right": {"type": "Number", "value": 2}}})
```

For a single-value `Literal[v]` (L5b), the synthesized clause is a bare `==` BinOp (no
`or` wrapper). For `Literal[None]`, the `== None` lowers to `== 0` at the IR level (the
existing None convention — `None` is int 0 in the IR; a `None` IR node also lowers to
`0`, but emitting a `Number 0` directly is byte-stable and matches the existing
`_csl_to_ir` path for `x == None`). For `Literal[True]` / `Literal[False]`, the IR
emits `Bool True` / `Bool False` and the existing binop-bool-as-int convention in
`expressions._handle_binop` (`expressions.py:432`–`435`) lowers `== True` to `= 1` and
`== False` to `= 0`.

### 1.3 Normalization steps (in order)

1. **Recognition** — at annotation-resolution time, detect `Literal[...]` on each
   `arg.annotation`, `node.returns`, and `AnnAssign.annotation`. *Implementation site:*
   a new helper `_normalize_literal_annotation(ann_expr, param_name)` invoked from
   `_m5_get_type_name` (`Module5_IREmitter.py:1790`) BEFORE the existing
   parametric-annotation branches, and from the return-annotation path
   (`:1932`–`:1956`). This keeps every unaffected driver byte-identical: annotations
   that are NOT `Literal[...]` skip the helper entirely (the helper returns `None` and
   the caller proceeds with the existing logic).

2. **Kind check (L4, L4a)** — for each literal value `v_i`:
   - `ast.Constant` with `value` of type `int`, `str`, `bool`, or `None` → accept (L4).
     (`bool` is a subtype of `int` in Python and in the IR — `True`→1, `False`→0.)
   - `ast.Constant` with `value` of type `bytes` → **REJECT** with a clear error
     `Literal: bytes literals are not supported (L4a / PEP 586)` (L4a). The error is
     raised from `_normalize_literal_annotation` so it surfaces as a PyCSL front-end
     error (the same channel as any other static rejection), NOT a Why3 type error.
   - `ast.Name(id="None")` → accept as `None` (some users spell `Literal[None]` with
     the bare name; PEP 586 permits both `None` the constant and `None` the name).
   - `ast.Name(id="True")` / `ast.Name(id="False")` → accept as the corresponding bool.
   - Any other form (`Literal[Literal[1, 2]]`, `Literal[X]` where `X` is a Name other
     than None/True/False, `Literal[f()]`, ...) → **REJECT** with
     `Literal: only int/str/bool/None literals are supported (L4 / L5c / PEP 586)`.
     This covers L5c (nested Literal) and L4b (Enum members — out of scope, rejected).

3. **Deduplication (L5a) + ordering (L5)** — the helper de-duplicates the value list by
   `(kind, value)` (so `Literal[1, 1]` → one value, `Literal["a", "a"]` → one value).
   Order is preserved (source order); L5 makes order irrelevant for the static judgment,
   so source order is a *rendering* detail only. The deduplication happens BEFORE the
   disjunction is synthesized, so the emitted `requires` has no duplicate disjuncts.

4. **Base type derivation** — the parameter's base type tag is:
   - `"int"` if every `v_i` is `int` / `bool` / `None` (the IR's int universe).
   - `"str"` if every `v_i` is `str`.
   - **REJECT** if the value list mixes `int` and `str` (e.g. `Literal[1, "a"]`). PEP
     586 permits mixed-kind literals in a single `Literal[...]`, but PyCSL's IR
     type-tag system is monomorphic per parameter — a parameter has one WhyML type, and
     Why3 has no `int \/ string` sum without a constructor. The two-plane spec §1.6
     allows sound expressibility to be STRICTER than S1; this is that strictness:
     `Literal[1, "a"]` is rejected with `Literal: mixed-kind literals (int + str) are
     not supported (PyCSL monomorphic parameter types)`. (A future enhancement could
     lower mixed-kind `Literal` to the Union sum-type seam — flagged in §8, NOT in this
     DRAFT.) This is the single deliberate S1-strictness for `Literal`.

5. **Synthesis** — the helper returns the base type tag (`"int"` or `"str"`), and as a
   side effect appends one IR expression dict to a per-function
   `_literal_requires` accumulator (a list on `self`). The caller (`_build_function_ir`)
   merges that accumulator into `func_ir["contracts"]["requires"]` AFTER the existing
   `csl_requires` IR list (so user-written `#@ requires` clauses come first, the
   synthesized Literal clause comes last — order within `requires` is logically
   conjunctive and commutative, so this is a rendering detail only).

6. **Return annotation** — for `def f(...) -> Literal[v1, ..., vn]`, the same synthesis
   applies, but the synthesized clause is an `ensures` on `\result` (not a `requires`
   on a parameter). The base type is the return type. *This is the dual of the parameter
   case.* The two-plane spec §1.1 L1 is stated for parameters; the return case is the
   obvious dual (`\result`'s value is one of `v1..vn`). The helper detects the
   `node.returns` form and emits an `ensures` clause instead.

### 1.4 Front-end files that change (on APPROVAL)

| File | Change |
|---|---|
| `src/pycsl/frontend/Module5_IREmitter.py` | add `_normalize_literal_annotation(ann_expr, param_name)` helper; call it from `_m5_get_type_name` (`:1790`) and the return-annotation path (`:1932`–`:1956`); merge the per-function `_literal_requires` / `_literal_ensures` accumulators into `func_ir["contracts"]` in `_build_function_ir`. For non-Literal annotations, the helper returns `None` and the caller falls through unchanged (byte-identical). |
| `src/pycsl/frontend/pure_ast.py` | NO change. `Literal[...]` already parses to `Subscript` (`:529`-area). The normalization runs on the AST, not the grammar. |
| `src/pycsl/frontend/Module1_Ingestor.py` | NO change. `Literal` is a Python annotation, not a `#@` directive. |
| `src/pycsl/frontend/import_classifier.py` | confirm `from typing import Literal` is canonicalized to the bare head name (already is). **Likely no change.** |

---

## 2. Lowering table entry (Module 6: `src/pycsl/module6_whyml/`)

### 2.1 The lowering

The synthesized `requires` clause lowers to a **Why3 precondition** (the two-plane spec
§1.6 names this exact mechanism as dischargeable):

```whyml
let function f (x: int)
  requires { (x = 1 \/ x = 2) }   (* synthesized from x: Literal[1, 2] *)
  ensures  { ... }                  (* user-written *)
= ...
```

where each `v_i` is the WhyML literal produced by the existing `_expr_to_whyml` path
for that IR node kind:
- `Number` → `1`, `2`, etc. (Why3 int literal).
- `String` → `"a"`, `"b"` (Why3 string literal; `use string.String` is auto-imported
  by `preamble.py` when a string-typed parameter is present — confirmed by the baseline
  `requires x == "a"` witness).
- `Bool` → lowered to `1` / `0` by the existing bool-as-int convention
  (`expressions.py:432`–`435`).
- `None` → lowered to `0` (the IR's int-None convention; `Literal[None]` is the
  singleton type of `None`, modeled as `requires { x = 0 }`).

This emission goes through the EXISTING `requires { ... }` path in
`module6_whyml/functions.py:273`–`274` — there is already a `requires { <expr> }`
emission seam, used today by every hand-written `#@ requires` clause.

### 2.2 Per-clause VC mapping (the load-bearing part)

Each static clause in the two-plane spec §1 maps to ONE VC or one normalization-time
check, generated by reusing existing Module 6 mechanisms — no new VC kind:

| Clause | Static obligation | VC / mechanism |
|---|---|---|
| **L1** (value set, load-bearing) | `x: Literal[v1, ..., vn]` ⟹ `x == v1 \/ ... \/ x == vn` | The synthesized `requires { x = v1 \/ ... \/ x = vn }` IS the VC. Why3 discharges it as a precondition goal (the caller must establish the disjunction before invoking `f`). Two S5 conformance cases: (a) a value equal to some `v_i` flows in (accept — the precondition is provable); (b) a value equal to no `v_i` flows in (reject — the precondition is unprovable, the call site VC fails). |
| **L2** (narrowing by equality) | `if x == v1:` on `x: Literal[v1, ..., vn]` → True-branch `x == v1`, False-branch `x == v2 \/ ... \/ x == vn` | Emergent from the standard path-condition VC: the synthesized `requires` is the disjunction, the `if x == v1:` test is the path condition, and Why3's standard precondition-preservation-on-branch refines the disjunction on each branch (True: `x = v1` is known; False: the `v1` disjunct is dropped). **No new node.** The runtime `==` test narrows the VALUE (LR5); the static narrowing is the path-condition VC (LD2 no-blend — the static narrowing does NOT require the runtime test to be executed, it is a proof-time judgment about the path). |
| **L2a** (chained equality narrowing) | repeated `if x == v_i:` tests narrow the residual set | Same as L2, applied repeatedly. Each test is a path condition that drops one disjunct. After all but one value is tested, the False branch narrows to the single remaining value. **No new node.** |
| **L2b** (`is None` for `Literal[None]`) | `if x is None:` narrows True→`Literal[None]`, False→residual | `is None` lowers to `== None` (the existing `Is`→`==` mapping, `Module5_IREmitter.py:982`), which lowers to `x = 0` (the None convention). The path-condition VC refines the `requires { x = 0 }` on the True branch. **No new node.** (For `Literal[None, 1]` — a mixed None+int Literal — the `is None` test narrows to the None arm; the `== 1` test narrows to the 1 arm. Both lower to `x = 0` / `x = 1` path conditions.) |
| **L3** (match/if-chain exhaustiveness) | a `match` or `if/elif`-chain on `x: Literal[v1, ..., vn]` must cover every `v_i` OR end with a catch-all | Emergent from the existing postcondition VCs: a non-exhaustive chain without a catch-all leaves a residual path where `x` is one of the un-tested `v_i` but no branch handles it → the postcondition VC fails on that path (the residual disjunction is still in the path condition, and the uncovered branch's postcondition is unprovable). A catch-all `else` covers the residual. **No new node, no new check.** (This is weaker than a dedicated exhaustiveness check — it catches uncovered values only when the postcondition is non-trivial — but it is sound: a non-exhaustive chain that happens to satisfy the postcondition is not a soundness bug, just a missed diagnostic. A dedicated exhaustiveness check is flagged for a future enhancement, §8.) |
| **L4** (supported literal kinds) | int / str / bool / None accepted | Normalization-time check (§1.3 step 2). Accepted kinds are lowered to the corresponding IR literal node. |
| **L4a** (bytes NOT supported) | `Literal[b"x"]` rejected | Normalization-time check (§1.3 step 2). REJECT with a clear error. |
| **L4b** (Enum members — separate concern) | `Literal[Color.RED]` rejected (out of scope) | Normalization-time check (§1.3 step 2 — any non-literal form is rejected). |
| **L5** (order-independent equality) | `Literal[1, 2]` == `Literal[2, 1]` | Normalization-time: the helper preserves source order but the static judgment is order-independent (the disjunction is commutative). No VC needed — two `Literal` types with the same value set produce logically equivalent `requires` clauses. |
| **L5a** (deduplication) | `Literal[1, 1]` == `Literal[1]` | Normalization-time (§1.3 step 3). The de-duplicated disjunction has no duplicate disjuncts. |
| **L5b** (single-argument degenerate) | `Literal[v]` is the singleton type of `v` | Normalization-time: a single-value `Literal[v]` synthesizes a bare `requires { x = v }` (no `or` wrapper). |
| **L5c** (no nested Literal) | `Literal[Literal[1, 2]]` rejected | Normalization-time check (§1.3 step 2 — a nested `Literal` is a `Subscript`, not a literal Constant, so it falls into the "any other form" rejection). |

### 2.3 The lowering seam (concrete file changes)

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/functions.py` | **No new path.** The existing `requires { ... }` emission (`:273`–`:274`) handles the synthesized clause. The existing `_param_type_str` / `_return_type` resolve the base type tag (`"int"` / `"str"`) — no change. |
| `src/pycsl/module6_whyml/expressions.py` | **No new path.** The existing `_handle_binop` (`:414`) handles `or` and `==`; the existing `_expr_to_whyml` paths for `Number` (`:1278`), `String` (`:654`), `Bool` (`:432`–`435`), `None` (via `== None` → `= 0`) handle each literal kind. |
| `src/pycsl/module6_whyml/preamble.py` | **No new path.** `use string.String` is auto-imported when a string-typed parameter is present (confirmed by the baseline `requires x == "a"` witness). |
| `src/pycsl/core_ir_semantic.py` | **No new check.** L4/L4a/L4b/L5c rejections happen at normalization time (front-end), not in the core. L3 exhaustiveness is emergent (§2.2). |

---

## 3. Shim contract (runtime plane: `src/pycsl_lib/typ/__init__.py`)

Per the two-plane spec §2 (LR1–LR8) and the no-blend rule (LD3), the runtime shim
constructs the introspectable object and performs **NO validation**. The current
`src/pycsl_lib/typ/__init__.py` already shims `cast` as an identity (`:11`–`:13`) and
`Union` as an identity (`:31`–`:33`); `Literal` follows the same discipline.

### 3.1 Shim surface

```python
# In src/pycsl_lib/typ/__init__.py — Literal alias construction, Shimmed (LR1–LR8).

#@ ensures \result == val       # LR3: no enforcement; the alias is the value.
def Literal(*args, val) -> int:  # returns the typing.Literal alias object
    return val                   # constructs the introspectable object (LR1, LR2)
```

(The `-> int` return tag is the existing PyCSL convention for opaque runtime objects —
the same convention `cast` and `Union` use. The WhyML model is `int`-typed and the
runtime object is opaque to the verifier; this is the established Modelled-for-identity
pattern.)

### 3.2 Contract discharges each LR-clause

| LR-clause | How the shim honours it |
|---|---|
| LR1 (alias object identity) | The shim returns the `val` (the runtime alias object is constructed by CPython's `typing.Literal` at the import site; the shim's responsibility is to NOT introduce a distinct class — LR8). |
| LR2 (introspection) | `get_origin`/`get_args` (already shimmed at `:21`–`:28`) return the alias's origin/args. **No change to those functions.** |
| LR3 (no enforcement) | The shim's `#@ ensures \result == val` carries ONLY the identity postcondition. There is no `requires` on the literal values. |
| LR4 (`isinstance` against `Literal` raises) | The shim does NOT make `Literal[1, 2]` a valid `isinstance` second argument. This is a runtime property of the alias object, not something the shim enforces — the alias object raises `TypeError` natively (S4). |
| LR5 (`x == v1` is the runtime test, NOT the static narrowing) | The shim does not touch `==`. The runtime `==` test is a value-level comparison the program performs; the static L2 narrowing is a proof-time path-condition judgment (LD2 no-blend). |
| LR6 (no annotation enforcement, even with `== v1`) | The shim's contract is identity only — it cannot enforce the annotation even if it wanted to (there is no `requires` clause on the literal values). |
| LR7 (no validation in the shim) | The shim performs NO check on whether `val` belongs to any literal value. A shim that DID check would be unfaithful in exactly the way an over-strong axiom is (LD3). |
| LR8 (`Literal` is not a distinct runtime class) | The shim does NOT introduce a distinct `Literal` runtime class; `Literal[v1, ..., vn]` must be the `typing.Literal` alias object, per LR1. |

### 3.3 Why the runtime shim does NOT discharge any static clause

This is the no-blend rule (LD3) made concrete: the shim's `ensures \result == val` is
SATISFIED by every value regardless of type. The static clauses L1–L5c are discharged by
the Why3 precondition VCs (§2.2), which are invisible to the shim. A conformance-agent
authoring the S5 subset from the two-plane spec + the shim surface alone cannot
reverse-engineer the lowering — the independence-based Gate C (c) holds.

---

## 4. Classification (`--soundness-report`)

Per the two-plane spec §4, the classification is **dual** (both planes, separately):

| Plane | Classification | Tag |
|---|---|---|
| Static | **Interpreted** | the annotation is consumed by the static plane and lowered to a ground `requires` obligation (per §2.2) |
| Runtime | **Shimmed** | the runtime meaning is the introspectable `typing.Literal` alias object, no enforcement (per §3) |

### 4.1 GT gap codes tagged for `Literal`

**No GT gap is tagged for `Literal`.** `Literal` is fully sound: the literal value set
is finite, enumerated, and decidable (L1's disjunction is finite; L2's narrowing refines
a finite set; L3's exhaustiveness is a coverage check over a finite enumeration). There
is no `Any`-style gradual-consistency concern (L4 restricts literal kinds to int/str/
bool/None), no variance, no `ParamSpec`/`TypeVarTuple`, no polymorphic recursion, no
forward-reference order beyond what TY0 owns, no `# type: ignore`, and no
runtime/static `Protocol`-style split. The no-blend discipline (LD2 — the runtime
`x == v1` test must not satisfy the L2 static narrowing obligation) is a `Literal`-local
specialization of the Union D2 / Optional OD2 no-blend rule, NOT a new GT code.

---

## 5. Standing gate plan (total additivity)

Per `typing-global-impl.md` §4 Gate B and the core-agent's hard rules:

### 5.1 Byte-identical emission for unaffected drivers

- The front-end normalization helper (`_normalize_literal_annotation`, §1.3) is a **pure
  function on the AST**: for any annotation that is NOT `Literal[...]`, it returns
  `None` and the caller proceeds with the existing logic unchanged. Every driver in the
  corpus that does NOT use `Literal` produces byte-identical IR and byte-identical
  WhyML.
- The corpus byte-diff gate (`bin/run-reference-tests.sh` / the standing gate) MUST
  remain green for every non-Literal driver. A byte-diff on an unaffected driver is a
  regression — the helper is mis-recognizing a non-Literal annotation.

### 5.2 `os` proof + `formal_<name>` suite re-confirmed

- The `os` library (fully green) does NOT use `Literal` annotations in its verified
  surface — confirm by `rg 'Literal\[' src/pycsl_lib/os/` before claiming additivity.
  (Expected: zero matches in verified code; any match is a comment-only reference.)
- The `formal_<name>` suite (json, re, warnings, …) is re-run; every previously-green
  formal test MUST remain green. A failure means the normalization helper is firing on
  a non-Literal annotation (the most likely regression mode).

### 5.3 IR-conformance corpora

- **No IR_VERSION bump.** The Literal construct reuses the EXISTING `contracts.requires`
  IR list and the EXISTING BinOp/Number/String/Bool/None IR expression nodes. No new IR
  field is introduced. `IR_VERSION` stays at its current value; `ACCEPTED_IR_VERSIONS`
  is unchanged. The IR-conformance corpora (core + front-end `*.ir.json` /
  `*.expected.mlw`) MUST remain green unchanged for every non-Literal driver.

### 5.4 doc-coherency green

- `test-suite/annotations.md`: add the canonical entry for the `Literal` annotation
  surface (citing S2 PEP 586). Per `pycsl-doc-coherency` skill, the entry must also
  appear in `docs/pycsl-concrete-syntax-reference.md`,
  `docs/pycsl-static-semantics-reference.md`, `docs/pycsl-translational-reference.md`,
  and a `config/skills/` skill (the `pycsl-annotate` skill already covers annotation
  surfaces). `bin/doc-coherency.py --check` MUST remain green. (Note: `Literal` is a
  Python annotation, not a `#@` directive — doc-coherency checks `#@` directives, so
  the `Literal` surface is documented in §12 of `annotations.md` alongside `Union` /
  `Optional`, and the three reference docs mirror that. The doc-coherency gate is green
  by construction for non-directive surfaces; the gate is re-run to confirm no
  directive-level drift was introduced.)

### 5.5 Non-vacuity gate (the load-bearing gate for Literal)

- The synthesized `requires { x = v1 \/ ... \/ x = vn }` VC MUST pass
  `--check-vacuity`. The VC is non-vacuous because the disjunction is satisfiable
  (each `v_i` is a concrete literal value, so `x = v_i` is satisfiable for `x = v_i`;
  the disjunction is the finite union of satisfiable cases). A false-twin (an
  impossible postcondition injected via `bin/false-twin.py`) on a function with a
  Literal precondition MUST FAIL — the precondition constrains the input but does not
  make the context inconsistent (the input space is non-empty: at least the `v_i`
  themselves satisfy the precondition).
- The witness driver `def f(x: Literal[1, 2]) -> int: return x` (gate item 5) exercises
  this: the synthesized `requires { x = 1 \/ x = 2 }` is non-vacuous (1 and 2 both
  satisfy it), and the postcondition `\result == x` discharges under the precondition.
- The narrowing driver `def f(x: Literal[1, 2]) -> int: if x == 1: return 0; return 1`
  (gate item 6) exercises L2: the True branch has `x = 1` (from the path condition) and
  returns 0; the False branch has `x = 2` (from the precondition's residual disjunct,
  since `x = 1` is ruled out) and returns 1. Both VCs discharge.

### 5.6 Witness / narrowing / bytes-rejection drivers (the coordinator's gate items 5–7)

| Gate item | Driver | Expected |
|---|---|---|
| 5 (witness) | `def f(x: Literal[1, 2]) -> int: return x` | lowers to `requires { x = 1 \/ x = 2 }`; VCs discharge (SUCCESS) |
| 6 (narrowing) | `def f(x: Literal[1, 2]) -> int: if x == 1: return 0; return 1` | VCs discharge (SUCCESS) — L2 narrowing via path-condition VC |
| 7 (bytes rejection) | `def f(x: Literal[b"x"]) -> int: return 0` | front-end REJECT with `Literal: bytes literals are not supported (L4a / PEP 586)` |

---

## 6. NoReturn × vacuity gate

**N/A for `Literal`.** The NoReturn × vacuity interaction (the sharpest TY1 obligation,
`typing-global-impl.md` §5 item 2) is owned by the **`NoReturn` construct's spec**, not
this one. A `NoReturn`-typed function carries a `false` postcondition by design; the
vacuity gate must exempt declared-`NoReturn` functions or it flags them as vacuous.

`Literal` does NOT interact with the vacuity gate in the NoReturn-specific way:
- A `Literal[...]` return type is NOT a `NoReturn` return type — it is a value-set
  constraint on `\result`. The synthesized `ensures { \result = v1 \/ ... \/ \result = vn }`
  is non-vacuous (each `v_i` is a concrete value, so the disjunction is satisfiable).
- A function declared `-> Literal[1, 2]` that returns a value other than 1 or 2 fails
  the synthesized `ensures` — that is a sound rejection, not a vacuity false-positive.
- **Cross-reference flag:** if a function's return type is `Literal[...]` AND the
  function is itself declared `NoReturn`, the two planes interact — the `NoReturn`
  spec's vacuity-gate exemption must apply. This edge case is noted here for the
  `NoReturn` spec to handle; `Literal`'s responsibility is only to emit the
  `ensures { \result = v1 \/ ... }` clause.

---

## 7. Deliverable checklist (on APPROVAL)

- [x] Front-end: `_normalize_literal_annotation` in `Module5_IREmitter.py`; wired into
      `_m5_get_type_name` and the return-annotation path. Per-function
      `_literal_requires` / `_literal_ensures` accumulators merged into
      `func_ir["contracts"]` in `_build_function_ir`.
- [x] Module 6: NO change (the existing `requires { ... }` / `ensures { ... }` paths
      handle the synthesized clauses).
- [x] `core_ir_semantic.py`: NO change (L4/L4a/L4b/L5c rejections happen at
      normalization time; L3 exhaustiveness is emergent).
- [x] `src/pycsl_lib/typ/__init__.py`: `Literal(*args, val)` shim (identity
      `ensures \result == val`).
- [x] `test-suite/annotations.md` (§12.9) + three reference docs; doc-coherency green.
- [x] `--soundness-report`: `Literal` classified Interpreted (static) / Shimmed
      (runtime) in the docs; the witness function classifies as Modelled (no
      `\trusted`, no `\abstract`); NO GT gap tag emitted.
- [x] Standing gate: corpus byte-diff green for all 618 non-Literal drivers
      (byte-identical); `os` proof + `formal_os_pure` re-confirmed; NO IR_VERSION
      bump; `--check-vacuity` green on the synthesized `requires`; witness (0731)
      + narrowing (0732) drivers SUCCESS; bytes-rejection driver (0733) ERROR
      (exit 1); false-twin (impossible `\result == 99`) FAILS (non-vacuous).
- [x] NO conformance-suite or shim-faithfulness-driver edits (the conformance-agent
      authors those, never the core-agent).

---

## 8. Open questions for the coordinator (editorial)

1. **Mixed-kind `Literal[1, "a"]`.** This DRAFT REJECTS mixed-kind literals (int + str
   in one `Literal[...]`) because PyCSL's parameter type-tag system is monomorphic.
   PEP 586 permits them. The two-plane spec §1.6 allows sound expressibility to be
   STRICTER than S1; this is that strictness. A future enhancement could lower
   mixed-kind `Literal` to the Union sum-type seam (25-1700-typing-spec-1) — i.e.
   `Literal[1, "a"]` becomes `Union[int, str]` with a per-arm `requires` — but that
   is NOT in this DRAFT. (Recommendation: reject for now; revisit if a driver needs it.)
2. **L3 exhaustiveness as a dedicated check.** This DRAFT makes L3 (match/if-chain
   exhaustiveness) emergent from the postcondition VCs (a non-exhaustive chain fails
   the postcondition on the uncovered path). A dedicated exhaustiveness check would
   catch non-exhaustive chains even when the postcondition is trivially satisfied.
   (Recommendation: emergent for now; a dedicated check is a future enhancement, not
   a soundness bug.)
3. **`Literal` in `AnnAssign`.** This DRAFT wires the helper into `_m5_get_type_name`
   (parameters + AnnAssign locals) and the return path. An `AnnAssign` with a
   `Literal` type (e.g. `x: Literal[1, 2] = 1`) synthesizes a `requires` on the
   local variable — but locals don't have `requires` clauses in PyCSL (only function
   parameters do). The helper detects the AnnAssign case and either (a) emits nothing
   (the `Literal` is a no-op on a local — the local's value is whatever it's assigned)
   or (b) emits an `assume`-style fact. (Recommendation: (a) for now — a local
   `Literal` is a type-system claim about the assigned value, which the initializer
   must satisfy; PyCSL has no `assume` mechanism, so the claim is unchecked on locals.
   This is a documented strictness, not a soundness bug — the local's value is
   whatever it's assigned, and the `Literal` claim is not used to refine anything.)
