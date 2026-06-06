# PyCSL Self-Annotation Plan — Status Snapshot

**Date:** 2026-05-27
**Source of truth:** `pycsl --keep-mlw <module>` (full proof), `make self-annotate-verify` (no-proof gate)
**Companion docs:** `docs/self-annotate-layer2-queue.md` (older queue, partially superseded), `my-llm-is-lazy.md` (Bucket A/B work), `remains-to-implement.md` (post-Phase-3 backlog)

## Trust chain (from README.md §"Trust Chain")

```
Layer 0 — Rocq / Lean type-checkers
   Machine-checked soundness theorem: pycsl_soundness
         ↓
Layer 1 — PyCSL #@ contracts on the Python implementation
   Structural faithfulness: frame conditions, loop termination,
   exhaustive dispatch over all 10 WP rule arms
         ↓
Layer 2 — Why3 + SMT solvers
   Output verification: the generated .mlw file is accepted by Why3
         ↓
Layer 3 — Why3 val spec module
   Semantic equivalence to Rocq fixpoint
```

## Current state

### Layer 1 (no-proof gate): ✅ green
- `make self-annotate-verify` passes for all 11 files in `src/self-annotate/src/`. (The historical `attic/rocq` and `attic/lean` mirrors were removed on 2026-05-27.)
- Proof-attribution audit: **162 PASS / 5 SKIP / 0 FAIL**.
- 12 cross-prover reference tests verify under full proof (0331, 0341–0351).
- pytest: 25 pass, 3 skip (3 pre-existing skill2rag failures excluded).

### Layer 2 (full proof per module): ⏳ all 7 modules still blocked

| Module | Blocker line | Shape | Severity |
|---|---|---|---|
| Module1_Ingestor | 48 | int vs `array int` — class G family (class-record where int expected) | Hard |
| Module2_Parser | 135 | termination warnings on recursive `_csl_to_str` — class I (no `\variant`) | Soft — type errors all cleared this session |
| Module3_Weaver | 133 | body-dict in `if X or Y:` bool context — `!d <> 0` doesn't type-check on map | Needs `_to_bool` fix for map-typed values |
| Module4_SemanticAnalyzer | 379 | Python set-union `held \| {mutex}` on map-typed param — needs set semantics or auto-trust | Needs auto-trust or Fset model |
| Module5_IREmitter | 119 | `'mu → option int` — likely body-return-type mismatch in `_build_function_ir` (84-line god method) | Needs investigation |
| Module6_WhyMLTranspiler | 434 | class M sub-case — `raise (Return (any_1 ...))` on array-returning expression | Needs auto-trust extension |
| ConcurrencyChecker | 61 | same set-union pattern as Module4 line 379 | Needs auto-trust or Fset model |

Line numbers may drift slightly as the source evolves; the BLOCKER SHAPE column is the durable identifier.

## What landed across the recent sessions (chronological)

### Pre-refactor session — Bucket A+B data structures
22 transpiler fixes shipped (queue doc classes A through R), with auto-`\trusted` workarounds for class M (array-typed Return), class O (heterogeneous tuple returns), and class R (dict-of-array). New reference tests 0345–0351 (body dict, body set, multi-arg range, Optional/Union, sorted/any/all).

### Refactoring pass 1
- Split all 5 functions >100 lines (`_emit_function`, `_handle_assign_stmt`, `transpile`, `_emit_body_code`, `_handle_binop`) into phase-based helpers.
- Removed unused `import re as _re` in pycsl.py.
- Tightened `except Exception` around `eval()` to specific eval-can-throw families.

### Refactoring pass 2
- Module6 `__init__` normalization: added 12 instance-attr initializations; removed all 40 defensive `getattr(self, '_attr', default)` patterns.
- Module3 `process()` split into `_parse_extracted_contracts` + `_consolidate_module_concurrency` + `_attach_labels_and_ghost_assigns`.
- Module3 `visit_FunctionDef` split into `_init_function_csl_fields` + `_dispatch_function_contracts` + `_validate_function_contracts`.

### Preamble fix
- `IRScanner.uses_inline_set_or_dict_ops` — detects set/dict literals and `.add()`/`.discard()`/`.remove()` calls anywhere in the IR, sets `needs_body_dict` even without var-binding. Unblocked ConcurrencyChecker's `held | {mutex}` triggering `map.Map` need.
- Reordered `use array.Array` to come AFTER `use map.Map` in preamble. Both modules provide `([])` operator; later import wins, so map.Map first means `arr[i]` resolves to `Map.get` (wrong). Fixed.

### Class D fix
- `_array_coerce_arg`: coerce int → `(Array.make 1 0)` placeholder when abstract vals expect `array int`.
- Context-aware `list_new`: emits `list_new_arr : int → array int` when surrounding function returns `array int`, else keeps `list_new : int → int`.
- `_bool_ir_to_int_wrap` extended to recognize `any(...)`/`all(...)` calls.
- `_coerce_to_int` extended for array-shaped AND map-shaped prefixes.
- `_emit_bitwise_or_power` coerces args via `_coerce_to_int`.
- For-loop iter detection for bare-name calls (not just `self.method(...)`).
- Class M sub-case for Set/Dict returns: new `_auto_trusted_map_returns` for functions with `-> Set[T]` / `-> Dict[K, V]` annotations.

### Module5 type inference (this session)
- `Module4._get_type_name`: extended for Subscript annotations (`Set[T]`, `Dict[K,V]`, `List[T]`, `Tuple[...]`, `Optional[T]`, `Union[T, None]`).
- `Module5._field_type_from_annotation` + `_collect_class_fields`: extracts field type from annotation; RHS-shape inference for `__init__` plain assignments.
- `Module4.visit_FunctionDef`: subscript-assign validator now allows `dict`/`Dict` (not just `list`/`List`/`Any`).
- `Module6._param_type_str` (both call sites): set/dict/frozenset → `map int (option int)`.
- `Module6._emit_type_decls`: record fields with type=set/dict/frozenset emit as `map int (option int)`; list/tuple → `array int`.
- `Module6._field_type_of`: resolves `self.<field>` (both `Attribute` and `FieldGet` shapes) via `_record_types["field_types"]`.
- `Module6._handle_array_set_stmt`: `self.<dict-field>[k] = v` emits `self.field <- map_update_some self.field k v`.
- `Module6._handle_subscript`: dict-typed self-field reads use match-on-Map.get.
- `Module6._emit_membership`: extended for map-typed receivers (params and self-fields).
- `Module6._build_method_param_types_map` + `_handle_dotted_call`: abstract `val` declarations now use real param types (no longer all-int); arg coercion picks the right shape per ptype.
- `Module6._rhs_yields_map` + `_collect_dict_var_assigns`: body locals whose RHS yields a map (via IfExpr, BinOp `|`/`&`/`-`, etc.) get tracked as `_dict_locals`.

## What's left (priority order)

### 1. Map-aware `_to_bool` (unblocks Module3 line 133)

The Python pattern `if d:` (truthy-on-dict) currently emits `!d <> 0` which fails on `map int (option int)`. Need `_to_bool` to detect map-typed values and emit something like `not (Map.is_empty d)` or check via `Fset.cardinal`. Workaround: rewrite the source to use `if d != {}:` or `if len(d) > 0:` patterns. Cleanest path is to extend `_to_bool` directly.

### 2. Auto-trust functions with set-union patterns (unblocks Module4 line 379, ConcurrencyChecker line 61)

Python `set1 | set2` (set union) is currently lowered to `bit_or set1 set2` (int OR), which loses the semantics. Two paths:

**Quick path (1–2h):** Auto-trust any function whose body has `BinOp(|/&/^/-)` between map-typed operands, similar to the existing class M / class O auto-trust patterns. Add `_auto_trusted_set_op_returns` list.

**Proper path (1–2 days):** Model `set | set` as `set_union` using Why3's `set.Fset` theory. Requires emitting `set_union (m1: map int (option int)) (m2: map int (option int)) : map int (option int)` as an abstract val with semantic ensures clause.

Recommendation: quick path first. The set semantics work belongs in a separate "proper set modeling" phase.

### 3. Module5 line 119 investigation (unblocks Module5)

The error "this expression has type `'mu → option int`, but expected int" at line 119 is inside `_build_function_ir` (84-line god method). Likely a Map-typed value flowing through a path that expects int. Needs the same kind of trace as I did for Module4 line 565.

### 4. Module6 line 434 (unblocks Module6)

The class M `any_1`-in-Return pattern. The Python code is `return any(...)` inside an `if` branch (so the Return goes through the exception mechanism, not direct return). The class M auto-trust fires for full-array-returning functions but not for individual `any_1` calls inside int-returning functions. Fix: extend `_bool_ir_to_int_wrap` to specifically detect `any_1`/`all_1` calls that need bool→int coercion at the Return site.

### 5. Module1 line 48 / class G (unblocks Module1)

`class-record where int expected`. The IR has a `pycslvisitor` record being passed where an int is expected. Likely the `Visit_X` dispatch table is typed as a record but used as int. Needs investigation — class G is the smallest unknown.

### 6. Module2 termination warnings (class I)

Module2's recursive `_csl_to_str` lacks `\variant` annotation. Either add `#@ \variant <expr>` or `#@ \diverges`. Not a hard error; Module2 type-checks correctly otherwise.

## What we are NOT doing (out of scope for now)

- **Set semantics via Fset**: deferred until set-union auto-trust path proves insufficient. Requires substantial WhyML theory work.
- **Proof-level type inference for `Tuple[*, *]` heterogeneous slots**: class O is already handled via auto-trust; per-slot inference would require threading IR-level type info through `find_return_type`.
- **Function-pointer dispatch in Module4** (`_PROTECTED_HANDLERS[type(node)]`): class H, fundamentally hard, needs a refactor of the dispatch mechanism.
- **List comprehensions (concrete)** and **enumerate/zip** as body-level constructs: tracked in `remains-to-implement.md`, deferred.

## Risk register

- **`make self-annotate-verify` could regress silently.** The gate runs `--no-proof`, so transpilation changes that emit invalid WhyML won't break it. Always run full-proof on a reference test (0342 is the canonical cross-validated example) after Module6 changes.
- **`src/self-annotate/src/*.py` is the only annotated mirror now.** The historical `attic/{rocq,lean}/` mirrors were removed on 2026-05-27.
- **Refactoring may drift queue-doc line numbers.** Treat the blocker SHAPE column as the durable identifier, not the line number.

## Suggested next session start

1. Take #2 (auto-trust set-union patterns) — quick path. Likely 2–4 module advance:
   - Module4 line 379 → next blocker (deeper or fully clear)
   - ConcurrencyChecker line 61 → next blocker
2. Then take #1 (`_to_bool` map-aware) to unblock Module3.
3. After those three modules clear: re-evaluate the queue and pick the lowest-effort remaining (probably #5 Module1 class G or #4 Module6 line 434).

## Working invariants

- **Always verify after each change:** `make self-annotate-verify` (Layer 1) + a sample of full-proof reference tests (0342 minimum, ideally 0345–0351 too) + pytest.
- **Single canonical mirror:** edits to `src/pycsl/*.py` may need a manual sync to `src/self-annotate/src/*.py` via `make sync-annotate-src`.
- **Module6 emission is the load-bearing surface:** Module5 type tags flow through to Module6's WhyML emission. New tags require both ends to be updated in sync.
- **Auto-trust is the safety valve:** when a Python pattern can't be cleanly modeled in WhyML (mutable types in exceptions, set semantics on maps, etc.), an auto-trust list (`_auto_trusted_array_returns`, `_auto_trusted_tuple_returns`, `_auto_trusted_map_returns`) preserves the Layer 1 contract without forcing a body emission that won't type-check.
