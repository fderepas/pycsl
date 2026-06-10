# The PyCSL IR — the front-end / core wire contract

**What this is.** The PyCSL IR is the serialized JSON intermediate representation that
sits on the seam between PyCSL's *front-end* (`src/pycsl/frontend/`, Modules 1–5 plus the
post-emission resolution passes) and its *language-agnostic core* (`src/pycsl/ir_schema.py`,
`core_ir_semantic.py`, `Module6_WhyMLTranspiler.py` + `module6_whyml/`). The front-end
ingests source, parses `#@` annotations, performs semantic analysis, and *emits* a single
JSON document (`ProgramIR`); the core *ingests* that document, runs language-agnostic
semantic checks on it, and lowers it to WhyML for Why3 / SMT discharge. Because the IR is
the only thing crossing this seam, it is the **front-end contract**: a second front-end —
Go via `go/ast`+`go/types`, C via Frama-C/ACSL — must produce exactly this shape for the
existing core to accept and correctly lower its programs. This document specifies that
shape precisely, derived entirely from the emitter (`frontend/Module5_IREmitter.py`), the
schema (`ir_schema.py`), the core reader (`core_ir_semantic.py`), the resolution passes
(`frontend/ir_resolve.py`), and real dumped IR from the reference corpus.

---

## 1. Overview & role

The IR is produced by `Module5_IREmitter.generate_json()` (`Module5_IREmitter.py:2049`),
which serializes a `ProgramIR` dict to indented JSON. It is consumed by the core in two
stages:

1. `validate_ir(ir)` — structural key-presence validation and version gate
   (`ir_schema.py:127`).
2. `run_ir_semantic_checks(ir)` — language-agnostic semantic checks
   (`core_ir_semantic.py:38`): source-span presence, `no_exception` well-formedness,
   assigns-region scope, contract-expression predicate/quantifier checks, contract scope
   and `\result` usage, subscript-assignment typing, checkpoint placement, mutable-default
   detection, acts validation, ghost string-op typing, and the cross-method HAPPY and
   mutex-invariant checks.

The core is **independently invokable** on a serialized IR with no front-end present. This
is proven by two conformance corpora and their runners:

- `bin/core-only-conformance.py` — for each `NNNN.ir.json` golden (a fully-resolved IR) in
  `test-suite/corpus/conformance/core/`, it loads the golden, runs `validate_ir` +
  `run_ir_semantic_checks`, transpiles via Module 6, and byte-diffs against
  `NNNN.expected.mlw`. It **asserts at import time that no front-end module
  (`Module1..5`, `pure_ast`) leaked into `sys.modules`** — the literal "core alone" claim.
- `bin/frontend-only-conformance.py` — the mirror: for each golden it re-derives the
  resolved IR from source (`bin/pycsl-ir-dump.py --resolved`) and structurally diffs
  against the frozen golden, asserting that no core / Module 6 / prover module is loaded
  after the front-end import.

### The "resolved IR" notion

The IR that Module 6 actually consumes is the **resolved** IR: the raw Module-5 emission
*after* four post-emission IR→IR passes run by `frontend.ir_resolve.resolve`
(`ir_resolve.py:704`), IN ORDER (`ir_resolve.py:713`):

1. `resolve_imports` — load dependency source files and inject the imported
   functions/classes the driver calls (marking them `trusted`).
2. `apply_inheritance` — monomorphize base-class methods onto subclasses.
3. `apply_composition` — Tier-1 `compose_from`/`mixin` flattening.
4. `apply_inline_globals` — inline method calls on module-level global instances.

**The wire IR is the RESOLVED IR.** A second front-end is free to perform its own
resolution however it likes, but the document it hands to the core must already be fully
resolved (every call resolves to an in-document function or an explicit stub). The
canonical way to obtain the wire IR is `bin/pycsl-ir-dump.py <source.py> --resolved`
(`bin/pycsl-ir-dump.py:45`); `--deep` recurses transitive imports.

---

## 2. Versioning & compatibility

Two top-level metadata keys stamp the IR as a versioned wire format
(`Module5_IREmitter.py:43`):

| Key | Value today | Meaning |
|-----|-------------|---------|
| `ir_version` | `"1.1"` | Semantic version of the IR schema this document conforms to (`ir_schema.py:35`, `IR_VERSION`). |
| `source_language` | `"python"` | The front-end that produced it. |

**Accepted versions.** `ACCEPTED_IR_VERSIONS = frozenset({"1.0", "1.1"})`
(`ir_schema.py:36`) is the exact set this core ingests.

**Compatibility policy (semver-style)** (`ir_schema.py:25–28`): MINOR bumps are **additive**
— new optional keys/nodes a newer core still ingests; a `"1.0"` IR remains ingestable by a
`"1.1"` core. MAJOR bumps are **breaking** — a removed or re-meaning'd key. Widen
`ACCEPTED_IR_VERSIONS` as additive versions land; drop a major when support ends. (The
`1.0 → 1.1` bump added the optional top-level `imports` key — `ir_schema.py:31–34`.)

**Enforcement** in `validate_ir` (`ir_schema.py:148–153`): if `ir_version` is present and
*not* in `ACCEPTED_IR_VERSIONS`, it is a **hard error** (do not lower an IR this core may
misread). An **absent** `ir_version` is tolerated as legacy/internal — but the real
pipeline always stamps it, so a conforming front-end MUST emit it.

> Front-end note: the front-end-only conformance runner treats a difference *confined to*
> `ir_version` as a non-fatal `VERSION-SKEW`, but any difference in actual content is a
> hard `MISMATCH`. The stamp is metadata; the program content below is the real contract.

---

## 3. Determinism requirement

The IR must serialize **canonically**: the same source must always produce byte-identical
JSON. No set-iteration order, hash-seed order, or dict-key nondeterminism may leak into the
output. This is a **hard front-end obligation** — the conformance corpora are byte- (core)
or structure- (front-end) frozen, and a nondeterministic emission breaks them.

The repo has fixed several such bugs by sorting at every set→list boundary. The relevant
example is `ir_resolve._process_dependency` (`ir_resolve.py:179–191`): the set of
transitively-`reachable` imported functions is **not** iterated directly (hash-seed
nondeterministic); instead it iterates `all_funcs` (insertion-ordered = source order) and
filters to `reachable`, giving a stable injected-function order for a multi-name import
like `from m import a, b`. Other set→list emissions in the emitter sort explicitly
(`array2d_params`, `array1d_params`, `seq_promoted_vars`, etc. — all `sorted(...)`).

A new front-end must apply the same discipline: any collection serialized into the IR must
have a deterministic, source-derived order.

---

## 4. Top-level structure — `ProgramIR`

`ProgramIR` is a `TypedDict(total=False)` (`ir_schema.py:83`). Validation requires only the
two structural keys; everything else is optional and present only when the source uses the
corresponding feature.

### Required keys (validated — `ir_schema.py:106`, `_REQUIRED_TOP`)

| Key | Type | Meaning |
|-----|------|---------|
| `type_decls` | `List[Dict]` | Declared types: `record` (classes/namedtuples) and `variant` (`#@ datatype`). See §4a. Empty list if none. |
| `functions` | `List[FunctionIR]` | Every emitted function/method (§5). Must be a list (`ir_schema.py:155`). |

### Optional metadata / interface keys

| Key | Type | When present | Meaning |
|-----|------|--------------|---------|
| `ir_version` | `str` | always (front-end MUST stamp) | §2. |
| `source_language` | `str` | always | §2. |
| `imports` | `List[List]` | module has imports | Each entry `[local, original, module, level, is_module]` (`Module5_IREmitter.py:97–111`). IR v1.1; consumed by import resolution, ignored by Module 6. Example: `[["double_int", "double_int", "multi_file_lib.arith", 0, false]]`. |
| `module_constants` | `Dict[str,int]` | module-level int constants (`K = 0`) | Name → literal int; resolved to the literal in Module 6 (`Module5_IREmitter.py:115`). |
| `module_globals` | `List[Dict]` | module-level `g = C(...)` instances | `{"name", "class", "value"}`; modeled as a Why3 mutable-record global (`Module5_IREmitter.py:131–136`). |
| `constructors` | `Dict[str,Dict]` | a `#@ datatype` is declared | Constructor registry: ctor name → `{"type", "arity"}` (`Module5_IREmitter.py:181`). |
| `inductive_decls` | `List[Dict]` | `#@ inductive` declared | `{"name", "signature", "rules":[(rule_name, clause_ir)], "members":[...]}` (`Module5_IREmitter.py:188`). |
| `compositions` | `List[Dict]` | `#@ compose_from` used | `{"composer", "mixins"}` (`Module5_IREmitter.py:1482`). |
| `happy` | `Dict` | module-level HAPPY properties | `{"properties":[{name,field,protects,except_set}], "method_names":[...], "exec_methods":[...]}` (`Module5_IREmitter.py:157`); drives the core's `_check_happy`. |

### Optional concurrency keys (present under `--memory-model concurrent`)

| Key | Type | Meaning |
|-----|------|---------|
| `shared_vars` | `List[Dict]` | `[{"name", "mutex"}]` — module-level shared variables (`Module5_IREmitter.py:78`). |
| `mutex_invariants` | `Dict[str,Dict]` | mutex name → invariant expr IR (`Module5_IREmitter.py:83`). |
| `thread_entries` | `List[str]` | function names tagged `#@ thread_entry` (`Module5_IREmitter.py:2035`). |
| `lock_order` | `List[str]` | declared lock ordering (`Module5_IREmitter.py:88`). |

### §4a. `type_decls` shapes

**record** (a class or namedtuple) — emitted by `visit_ClassDef`
(`Module5_IREmitter.py:1510`). Verified shape from
`test-suite/corpus/conformance/core/0441.ir.json`:

```json
{
  "kind": "record", "name": "Counter",
  "fields": [{"name": "start", "type": "int", "mutable": true}],
  "class_invariants": [ /* expr IR, e.g. self.start >= 0 */ ],
  "field_defaults": {"start": 7},
  "has_hash": false, "has_eq": false, "is_unhashable": false,
  "constants": {}, "bases": [],
  "init_params": [], "init_body": [],
  "is_mixin": false, "compose_from": []
}
```

Field `type` ∈ `int` | `list` | `dict` | `set` | `str` (`_field_type_from_annotation`,
`Module5_IREmitter.py:1264`; container shapes inferred from RHS in `_collect_class_fields`).

**variant** (a `#@ datatype`) — emitted at `Module5_IREmitter.py:174`:

```json
{
  "kind": "variant", "name": "Option",
  "type_params": ["T"],
  "constructors": [{"name": "None_", "arity": 0, "payload": []},
                   {"name": "Some", "arity": 1, "payload": ["int"]}]
}
```

---

## 5. `FunctionIR`

One entry per function/method in `functions`. Method names are flattened to
`Class__method` (lower-cased class, `Module5_IREmitter.py:1681`). Built by
`_build_function_ir` (`Module5_IREmitter.py:1679`).

### Required fields (validated — `ir_schema.py:108`, `_REQUIRED_FUNCTION`)

| Field | Type | Meaning |
|-------|------|---------|
| `name` | `str` | Function name (`Class__method` for methods). |
| `symbol_table` | `Dict[str,str]` | Local-scope name → type tag. Built by `_build_function_symbol_table` (`Module5_IREmitter.py:1610`): params (skip `self`) → `Assign`/`AnnAssign`/`For` locals (skip shared vars) → ghost-var declarations, in that **insertion order**. Type tags are Python type names or `"Any"`. |
| `return_annotation` | `str` \| `null` | Return type; parametric heads lower-cased (`List[str]`→`"list"`), `Optional[T]`/`Union[T,None]` unwrapped (`Module5_IREmitter.py:1690`). |
| `contracts` | `ContractsIR` | §6. |
| `body` | `List[Dict]` | Statement nodes (§8). |
| `function_variants` | `List[Dict]` | Termination measures for the function: each `{"expr": <expr-IR>, "ordering"?: str}` (`Module5_IREmitter.py:435`). |
| `diverges` | `bool` | `#@ diverges` (non-terminating). |
| `trusted` | `bool` | `#@ \trusted` (assume contract, no body proof); also set on injected imports. |
| `bounded_int` | `int` \| `null` | `#@ bounded_int N` bit width, else `null`. |

### §4.4 source-span contract (enforced by the core)

Every function MUST carry `line` and `col` (`Module5_IREmitter.py:2027`). The core's
`_check_span` (`core_ir_semantic.py:64`) raises if `line` is missing — *"a front-end must
stamp §4.4 spans (line/col) on every node"*. Loop statements (`While`/`For`) additionally
carry their own `line` (`Module5_IREmitter.py:1134`, `:1145`), used to reconstruct
`"while loop at line N inside function 'F'"` error contexts.

### Optional fields

| Field | Type | Meaning |
|-------|------|---------|
| `line`, `col` | `int` | §4.4 source span (always emitted by this front-end; `line` is effectively required). |
| `formal_params` | `List[str]` | Formal parameter names only (excludes `self` and locals) — Module 6 uses this for parameter-mutation handling. |
| `param_defaults` | `Dict[str,expr-IR]` | Positional default values, name → default expr (`Module5_IREmitter.py:1746`); lets a short call fill trailing params. |
| `has_mutable_default` | `bool` | Any default arg is a list/dict/set literal or `list()/dict()/set()` call (`Module5_IREmitter.py:1760`); the core's `_check_mutable_defaults` raises on it. |
| `acts` | `List[Dict]` | Pre-desugar `#@ act` metadata for `_check_acts`: `{"kind":"act","name","given_exprs":[...]}`, `{"kind":"complete","names":[...]}`, `{"kind":"disjoint","names":[...]}` (`Module5_IREmitter.py:1771`). |
| `dict_value_types`, `dict_key_types` | `Dict[str,str]` | WhyML value/key types for string-valued dicts (`Module5_IREmitter.py:1792`). |
| `pure` | `bool` | Detected purity (`_detect_purity`). |
| `memoized` | `bool` | Has a memoizing decorator (`Module5_IREmitter.py:1835`). |
| `array1d_params`, `array2d_params` | `List[str]` | Params accessed as 1-D / `a[i][j]` arrays, **sorted** (`Module5_IREmitter.py:1882`, `:1916`). |
| `seq_promoted_vars`, `seq_promotion_conflicts` | `List[str]` | Growable-list analysis metadata, **sorted** (`Module5_IREmitter.py:2013`); diagnostics-only. |
| `no_inline` | `bool` | `#@ no_inline` modular boundary. |
| `abstract` | `bool` | `#@ \abstract` (opaque `val`). |
| `preserves` | `bool` | `#@ \preserves` HAPPY trust boundary. |
| `lemma` | `bool` | `#@ lemma` function. |
| `uses` | `List[str]` | `#@ uses` referenced lemma/predicate names. |
| `interface` | `Dict` | Track-B narrow opacity contract `{requires,ensures,assigns}` or `{}` if transparent (`Module5_IREmitter.py:1822`). |
| `reveal` | `List[str]` | `#@ reveal` names. |
| `reviewer` | `str` | `#@ reviewer` attribution. |
| `proof` | `List[Dict]` | `#@ proof` citations `[{"prover","qualname"}]` → Why3 `axiom` block (`Module5_IREmitter.py:1841`). |
| `provides`, `method_deps`, `shared_state`, `touches_field` | various | Tier-1 mixin-composition metadata (`Module5_IREmitter.py:1852–1863`). |
| `thread_entry` | `bool` | `#@ thread_entry` (also adds name to top-level `thread_entries`). |
| `kind` | `str` | `"method"` for class methods (`Module5_IREmitter.py:2039`). |
| `self_type` | `str` | The class name for a method. |

---

## 6. `ContractsIR`

The `contracts` sub-dict of a `FunctionIR` (`ir_schema.py:46`). `validate_ir` requires the
first four keys (`ir_schema.py:120`, `_REQUIRED_CONTRACTS`).

| Key | Type | Shape | Required? |
|-----|------|-------|-----------|
| `requires` | `List[expr-IR]` | Precondition expression nodes (§7). | yes |
| `ensures` | `List[expr-IR]` | Postcondition nodes; the **only** clause where `Result` is allowed (`core_ir_semantic.py:302`). | yes |
| `assigns` | `List[expr-IR]` | Frame targets — a flat list of expr nodes, one per assigned target (`Module5_IREmitter.py:1799`). | yes |
| `raises` | `List[Dict]` | `[{"exc_type": str, "condition": <expr-IR>}]` (`Module5_IREmitter.py:1800`). | yes |
| `no_exception` | `List[str]` | Exception names the function commits not to raise (`Module5_IREmitter.py:1806`). Absence ≡ `[]`. | no |
| `no_exception_all` | `bool` | `#@ no_exception \all` mode. Absence ≡ `false`. | no |

Each clause IR may carry an `act_name` string (`Module5_IREmitter.py:691`) when it was
desugared from an `#@ act`, so Module 6 can emit a `(* act NAME *)` comment.

---

## 7. Expression node types

Every expression node is a dict with a `"type"` discriminator. The table below covers all
node types the emitter produces and the core reads. The core's scope/predicate walks
(`_ir_free_vars`, `_pb_expr`, `_contains_result` — `core_ir_semantic.py:373`, `:232`, `:486`)
dispatch on these; nodes not listed there recurse generically (the core treats `FieldGet`,
`Result`, `Attribute`, `Call` as **opaque to scope extraction** — `core_ir_semantic.py:390`).

### Core / arithmetic / logic

| `type` | Fields | Meaning / WhyML lowering |
|--------|--------|--------------------------|
| `Var` | `name` | A variable reference; the only node `_ir_free_vars` treats as a free var. |
| `Number` | `value` | Integer/numeric literal. |
| `String` | `value` | String literal → Why3 `string`. |
| `Bool` | `value` | Boolean literal. |
| `None` | — | Python `None`, modeled as `0`. |
| `Nothing` | — | The empty `\nothing` assigns target. |
| `BinOp` | `op`, `left`, `right` | Binary op; `op` is the string form (`+ - * / div % == != < <= > >= and or ==> in & \| ^ << >> **`). Comparison/`BoolOp` chains are flattened into nested `BinOp` (`Module5_IREmitter.py:785`, `:789`). |
| `UnaryOp` | `op`, `expr` | Unary op (`- + not ~`). |
| `IfExpr` | `test`, `body`, `orelse` | Conditional expression. |
| `Old` | `expr` | `\old(e)` — pre-state value. |
| `OldField` | `object`, `field` | Flattened `\old(self.f)` (`Module5_IREmitter.py:352`). |
| `Result` | — | `\result`; only legal in `ensures` (`_contains_result`). |
| `At` | `expr`, `label` | `\at(e, L)` labeled value. |

### Member / call / index

| `type` | Fields | Meaning |
|--------|--------|---------|
| `FieldGet` | `object` (`"self"`), `field` | `self.f` (a mutable record field). Opaque to scope extraction. |
| `Attribute` | `object` (expr-IR), `attr` | `p.f` on a record-typed param, or `\result.f` (object is `{"type":"Result"}`); `Module5_IREmitter.py:313`. |
| `Call` | `func` (str), `args`, `receiver`? | Function/method call; dotted calls keep the dotted name in `func`, an unresolved receiver expr goes in `receiver` (`Module5_IREmitter.py:796`). |
| `Subscript` | `value` (expr-IR), `index` (expr-IR) | `a[i]`. `value` may be `Result`, a `Var`, or a nested `Subscript`/`FieldGet` for `a[i][j]` / `self.f[i]`. |
| `SliceAccess` | `value`, `slice` (a `Slice` node) | `a[lo:hi]`. |
| `Slice` | `lower`, `upper`, `step` (any may be `null`) | A slice spec. |

### Memory-model predicates

| `type` | Fields | Meaning |
|--------|--------|---------|
| `ArrayLen` | `var` (str) | `\length(a)`. Core rejects it on dict/set types (`core_ir_semantic.py:243`). |
| `Valid` | `base` (str), `length` (expr-IR) | `\valid(a, n)`; `base` must be a list/bytes param (`core_ir_semantic.py:254`). |
| `Separated` | `base1`, `len1`, `base2`, `len2` | `\separated(a, na, b, nb)`. |
| `AssignsRegion` | `base` (str), `low`, `high` (expr-IR) | An `a[low..high]` frame region. |
| `Length2D` | `base`, `rows`, `cols` | 2-D length predicate. |
| `Valid2D` | `base`, `row`, `col` | 2-D validity predicate. |
| `InGlobals` | `name` | `\in_globals(x)`. |
| `InScope` | `name` | `\in_scope(x)`. |

### Quantifiers

| `type` | Fields | Meaning |
|--------|--------|---------|
| `Forall` | `var`, `body`, `binder_type`?, `domain`? | `\forall`. `binder_type` (optional) is the typed binder; the core rejects an unresolved type (`core_ir_semantic.py:270`). `domain` (optional) bounds the binder. |
| `Exists` | `var`, `body`, `binder_type`?, `domain`? | `\exists`. |
| `ForallItems` | `key`, `val`, `map` (str), `body` | Two-binder dict-items quantifier (`Module5_IREmitter.py:370`) → Module 6 `match`. |

### Tuples & algebraic data (structural invariant — see below)

| `type` | Fields | Meaning |
|--------|--------|---------|
| `MkTuple` | `elts` (list) | Tuple constructor. |
| `Tuple` | `elts` (list) | Python tuple literal (body path). |
| `FstExpr` | `tuple` | First projection of a pair. |
| `SndExpr` | `tuple` | Second projection of a pair. |
| `ProjExpr` | `tuple`, `index` (**int literal**) | n-th projection. **`index` is an `int`, not an expr** (`Module5_IREmitter.py:562`: `int(node.index.value)`). |
| `CtorTest` | `var`, `ctor` | `\is_ctor(x, C)` variant tag test. |
| `CtorPayload` | `var`, `ctor`, `index` | The i-th payload field of a variant value. |

> **Structural invariant the core relies on:** `ProjExpr.index` MUST be a literal integer.
> Dynamic projection is unsupportable in a WhyML tuple (tuple components are positional, not
> indexable by a runtime value), so the front-end resolves the index to a literal at emit
> time. The Module-4 check that `\proj`'s index is a literal is deliberately **not migrated**
> to the core (`core_ir_semantic.py:279–283`) because it is a *precondition* the emitter
> depends on — it must run before emission. A new front-end MUST guarantee this.

### Strings

| `type` | Fields | Meaning |
|--------|--------|---------|
| `StrConcat` | `left`, `right` | String concatenation. |
| `StrLength` | `string` | String length. |
| `StrSub` | `string`, `lo`, `hi` | Substring. |
| `FString` | `parts` (list) | f-string (body path). |

### Ghost / array values

| `type` | Fields | Meaning |
|--------|--------|---------|
| `GhostCopy` | `arr` (str) | `\copy(a)` — snapshot of an array (`Module5_IREmitter.py:584`). |
| `GhostCopyRange` | `arr` (str), `lo`, `hi` | `\copy(a, lo, hi)`. |
| `GhostMake` | `size`, `default` | `\make(n, v)` array constructor. |
| `ArrayLit` | `elts` (list) | List literal / bytes literal (body path; bytes → ints). |
| `MapValueIs` | `map` (str), `key`, `value` | Synthesized: "value stored under some key" (from `v in d.values()`, `Module5_IREmitter.py:498`). |

### Maps / dicts

| `type` | Fields |
|--------|--------|
| `MapEmpty` | — |
| `MapGet` | `dict`, `key` |
| `MapSet` | `dict`, `key`, `value` |
| `MapEq` | `left`, `right` |
| `HasKey` | `dict`, `key` |
| `MapRemove` | `dict`, `key` |
| `DictLit` | `keys`, `values` (body path) |
| `DictComp` | `key`, `value`, `generators` (body path) |

### Sets

| `type` | Fields |
|--------|--------|
| `SetEmpty` | — |
| `SetAdd` | `set`, `elem` |
| `SetRemove` | `set`, `elem` |
| `SetMem` | `elem`, `set` |
| `SetUnion` / `SetInter` / `SetDiff` | `left`, `right` |
| `SetCard` | `set`, `lo`, `hi` |
| `SetSubset` / `SetEq` | `left`, `right` |
| `SetLit` | `elts` (body path) |
| `SetComp` | `elt`, `generators` (body path) |

### Lists (functional cons-list model)

| `type` | Fields |
|--------|--------|
| `Nil` | — |
| `Cons` | `head`, `tail` |
| `Hd` | `list` |
| `Tl` | `list` |
| `ListLength` | `list` |
| `Nth` | `list`, `index` |
| `Mem` | `elem`, `list` |
| `Append` | `left`, `right` |
| `ListComp` | `elt`, `generators` (body path) |

### Array/sequence predicates (contract sugar)

| `type` | Fields |
|--------|--------|
| `IsSorted` | `base`, `lo`, `hi` |
| `ArrayEq` | `left`, `right` |
| `Permutation` | `left`, `right` |
| `Sum` | `base`, `lo`, `hi` |

### Body-only Python-expression nodes

These appear in statement `body` / executable contexts (produced by `_py_expr_to_ir`):
`Starred` (`value`), `NamedExpr` (`target`, `value` — walrus), `Lambda` (`params`, `body`).
`UnknownPyExpr` (`Module5_IREmitter.py:743`) is the fallback for an unhandled Python
expression — a new front-end should never emit it for a supported construct; its presence
signals an out-of-subset expression.

> Desugaring note: `x in coll` is **not** a single node. The emitter (`_csl_in`,
> `Module5_IREmitter.py:463`) desugars it at emit time: an integer-`range` becomes a
> `lo <= x and x < hi` `BinOp`; a set/dict/str collection becomes a raw `{"op":"in"}`
> `BinOp` (lowered by Module 6's membership emitter); an array becomes an
> `Exists` over indices. `x not in coll` becomes `UnaryOp(not, <in>)`.

---

## 8. Statement node types

Every body statement is a dict with a `"stmt"` discriminator (`_py_stmts_to_ir`,
`Module5_IREmitter.py:936`). The core walks them in `_pb_stmt` (`core_ir_semantic.py:186`),
descending into nested lists for compound statements.

| `stmt` | Fields | Meaning |
|--------|--------|---------|
| `Assign` | `target` (str), `value` (expr-IR) | `x = e`. |
| `AugAssign` | `target`, `op`, `value` | `x op= e`. |
| `FieldAssign` | `object` (`"self"`), `field`, `value` | `self.f = e`. |
| `FieldAugAssign` | `object`, `field`, `op`, `value` | `self.f op= e`. |
| `ArraySet` | `array` (expr-IR), `index` (expr-IR), `value` (expr-IR) | `a[i] = e`; nested `array` Subscript for `a[i][j]`. The core's `_check_subscript_assignments` validates the base type. |
| `ArraySliceSet` | `array`, `lower`, `upper`, `value` | `a[lo:hi] = e` → bounded `Array.blit`. |
| `TupleUnpack` | `targets` (list[str]), `value` | `a, b = e`. |
| `Return` | `value` (expr-IR or `null`) | `return e` / bare `return`. |
| `If` | `test`, `body` (list), `orelse` (list) | `if/else`. |
| `While` | `line`, `test`, `invariants` (list), `variants` (list), `body` (list) | `while`. Carries §4.4 `line`; `invariants`/`variants` are clause-expr lists checked by the core. |
| `For` | `line`, `lineno`, `target` (str), `iter`, `invariants`, `variants`, `body`, `allow_iteration_mutation` (bool) | `for`. Same invariant/variant treatment as `While` (`core_ir_semantic.py:195`). |
| `Continue` / `Break` / `Pass` | — | Loop control / no-op. (`del` also lowers to `Pass`.) |
| `Assert` | `test`, `msg`? | Python `assert` (a no-op for verification — distinct from `ProofAssert`). |
| `ProofAssert` | `kind` (`"assert"`/`"check"`), `test` (expr-IR), `origin`? | `#@ assert P` / `#@ check P` — a real proof obligation before the statement (`Module5_IREmitter.py:944`). |
| `GhostAssign` | `target` (str), `value` (expr-IR), `op` (`"="`/`"+="`/…), `ghost_type` | Ghost variable declaration/update (`Module5_IREmitter.py:969`). |
| `GhostArraySet` | `target` (str), `index` (expr-IR), `value` (expr-IR) | Ghost array element set (`Module5_IREmitter.py:966`). |
| `Raise` | `exc_type` (str or `null`), `exc_value` (expr-IR or `null`) | `raise E(v)`. |
| `Try` | `body`, `handlers` (`[{exc_type,name,body}]`), `orelse`, `finalbody` | `try/except/else/finally`. |
| `With` → `CriticalSection` | `mutex`, `body`, `assume_invariant`, `prove_invariant` | A `#@ critical`/`acquires` `with` block (`Module5_IREmitter.py:1102`); a plain `with` is flattened into its body. |
| `Match` | `subject`, `cases` (`[{pattern,guard,body}]`) | `match` (patterns: `Value`/`Wildcard`/`Capture`/`Or`/`Sequence`/`Constructor`, `Module5_IREmitter.py:1165`). |
| `Expr` | `value` (expr-IR) | A bare expression statement (docstring string-literals are dropped). |
| `Label` | `name` | A `#@ ghost`/label marker emitted before a statement (`Module5_IREmitter.py:940`). |

---

## 9. Front-end obligations checklist

A new front-end (Go, C, …) that produces this IR for the existing core must guarantee:

1. **Version stamp.** Emit `ir_version` ∈ `ACCEPTED_IR_VERSIONS` (currently `"1.0"`/`"1.1"`)
   and a `source_language` tag. An unrecognized stamped version is a hard reject.
2. **Required keys.** Top-level `type_decls` and `functions` (a list). Each function:
   `name`, `symbol_table`, `return_annotation`, `contracts`, `body`,
   `function_variants`, `diverges`, `trusted`, `bounded_int`. Each `contracts`:
   `requires`, `ensures`, `assigns`, `raises` (`validate_ir`, `ir_schema.py:108–120`).
3. **Source spans on every function.** `line` (and `col`) — the core's `_check_span`
   rejects a function without `line`. Loop statements carry their own `line` for error
   context.
4. **Canonical / deterministic serialization.** No set/hash-ordering may leak into the
   output; sort every set→list boundary by a source-derived key (§3). Resolved
   import-injection order in particular must be source order, not set order.
5. **Resolved IR.** Hand the core the *resolved* document: imports injected, inheritance
   monomorphized, composition flattened, global method-calls inlined — every `Call`
   resolves to an in-document function or an explicit `trusted`/`abstract` stub.
6. **`ProjExpr.index` is a literal int** (not an expression). Resolve dynamic projections
   at emit time or reject them; the core does not re-check this.
7. **`symbol_table` types** must classify each name well enough for the core's predicate
   checks: `\length`/`\valid`/`\separated` bases must be list/bytes-typed (the core rejects
   them on dict/set/scalar, `core_ir_semantic.py:243–269`); typed quantifier binders must
   name a known type (scalar, declared datatype, or class, `core_ir_semantic.py:270`).
8. **`\result` only in `ensures`.** The core enforces this (`core_ir_semantic.py:302`).
9. **Contract scope.** Every variable in a contract expr must be in the function's
   `symbol_table` or a `module_constant` (`core_ir_semantic.py:290`).
10. **`no_exception` well-formedness.** Names must be known exceptions and must not
    contradict `raises`/`no_exception_all` (`core_ir_semantic.py:77`).
11. **No `UnknownPyExpr`/`Unknown` nodes** for supported constructs — they signal an
    out-of-subset expression the core cannot lower.

---

## Worked example (verified)

From `bin/pycsl-ir-dump.py test-suite/corpus/pycsl-reference/0001.py`, the function
`test_precondition(x) -> int` with `requires x >= 0`, `ensures \result >= 0`,
body `return x + 1`:

```json
{
  "ir_version": "1.1", "source_language": "python",
  "type_decls": [],
  "functions": [{
    "name": "test_precondition",
    "symbol_table": {"x": "int"},
    "formal_params": ["x"],
    "return_annotation": "int",
    "contracts": {
      "requires": [{"type": "BinOp", "op": ">=",
                    "left": {"type": "Var", "name": "x"},
                    "right": {"type": "Number", "value": 0}}],
      "ensures":  [{"type": "BinOp", "op": ">=",
                    "left": {"type": "Result"},
                    "right": {"type": "Number", "value": 0}}],
      "assigns": [], "raises": [],
      "no_exception": [], "no_exception_all": false
    },
    "body": [{"stmt": "Return",
              "value": {"type": "BinOp", "op": "+",
                        "left": {"type": "Var", "name": "x"},
                        "right": {"type": "Number", "value": 1}}}],
    "function_variants": [], "diverges": false, "trusted": false,
    "bounded_int": null, "line": 5, "col": 0
  }]
}
```

---

## 10. Stability, versioning & freeze

**The IR is FROZEN at v1.1 as the published front-end ↔ core contract.** With Phase E
complete (`refactor.md`), this document — together with `ir_schema.py` (`IR_VERSION`,
`ACCEPTED_IR_VERSIONS`) and the two conformance corpora — is the *stable target* a second
front-end is developed against. The shape specified in §§4–8 and the obligations in §9 do
not change underneath an implementer: any change to them is a *versioned* event governed by
the policy below, not an ambient drift.

### 10.1 Compatibility policy (normative)

Versioning is semver-style (`ir_schema.py:25–28`; restated here as the published policy):

- **MINOR bump** (e.g. `1.1 → 1.2`) is **additive and back-compatible**: it may add new
  optional top-level keys, optional `FunctionIR`/`ContractsIR` fields, or new node types,
  but must never remove or re-mean an existing key. A document valid under the lower minor
  remains valid under the higher one, so the lower version stays in `ACCEPTED_IR_VERSIONS`.
  The `1.0 → 1.1` bump (the optional `imports` key) is the worked precedent.
- **MAJOR bump** (e.g. `1.x → 2.0`) is **breaking**: it removes or re-means a key, or
  tightens a shape. It requires deliberately **widening** `ACCEPTED_IR_VERSIONS` (to ingest
  both old and new for a migration window) and later **retiring** the old major when support
  ends. A stamped-but-unaccepted `ir_version` is a hard reject in `validate_ir`
  (`ir_schema.py:148–153`) — the core never lowers an IR it may misread.

Any change to this document that alters the wire shape MUST be accompanied by the matching
`IR_VERSION` bump and an `ACCEPTED_IR_VERSIONS` update, and MUST keep the conformance
corpora green (§10.2). The version field is the single source of truth for "which contract".

### 10.2 The two conformance corpora ARE the contract test

The contract is not merely documented — it is **regression-tested** by the two corpora in
`test-suite/corpus/conformance/`, run by the gate (see `bin/run-conformance.sh`, wired into
`bin/run-reference-tests.sh`):

- **Core corpus** (`bin/core-only-conformance.py`): the **core honors the IR with no
  front-end**. For each frozen `NNNN.ir.json` golden it runs `validate_ir` +
  `run_ir_semantic_checks` + Module 6 and **byte-diffs** against `NNNN.expected.mlw`, with
  an import-time assertion that no `Module1..5`/`pure_ast` module loaded. A core change that
  breaks golden-IR → WhyML fails here.
- **Front-end corpus** (`bin/frontend-only-conformance.py`): the **Python front-end produces
  the canonical IR with no prover**. For each golden it re-derives the resolved IR from
  source (`--resolved`) and **structurally diffs** against the frozen golden, asserting no
  core / Module 6 / prover module loaded. A front-end change that breaks source → IR fails
  here.

Together they pin both halves of the seam: golden IR ⇄ both the WhyML the core must emit and
the IR the front-end must emit. A change that moves either half without a version event
breaks the gate by design.

### 10.3 Obligation on a NEW front-end

A second front-end — **Go** (via `go/ast` + `go/types`) or **C** (via Frama-C/ACSL) — is now
developable against a stable target. To be conformant it MUST:

1. **Target this document** (`docs/ir.md`): produce a `ProgramIR` of exactly the shape in
   §§4–8, honoring every obligation in §9 (version stamp, required keys, source spans,
   resolved IR, literal `ProjExpr.index`, contract scope, `no_exception` well-formedness, no
   `Unknown` nodes for supported constructs).
2. **Emit a canonical, deterministic serialization** (§3): no set/hash-iteration order may
   leak into the output; every set→list boundary is sorted by a source-derived key. The
   front-end corpus's PYTHONHASHSEED determinism gate enforces this for the Python front-end,
   and any new front-end must hold to the same byte-stability discipline.
3. **Pass the front-end corpus** as its acceptance bar: re-deriving the IR for the reference
   drivers must structurally match the frozen goldens (modulo the `ir_version` stamp, which
   is reported as non-fatal `VERSION-SKEW`). Passing the front-end corpus is the operational
   definition of "this front-end produces the canonical IR" — the existing core then accepts
   and correctly lowers its programs unchanged, which the core corpus already guarantees.
