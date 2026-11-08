# Triage A4 — core semantic + IR-resolution passes (self-tcb-reduction frontier)

READ-ONLY triage. No conversions, no commits. Method: static classification against the
recognizer stack + known-gaps, one confirming spot-check (`_method_key`, L3-tc ✓, reverted).

Stub counts are the `^#@ .trusted` markers in the MIRROR (`src/self-annotate/src/…`); the
transcription source is the LIVE method in `src/pycsl/…`. Brief's "139" was approximate; the
real total is **126** (mirror is slightly behind live — e.g. `collect_module_const_dicts` is a
newer live fn not yet in the mirror, so it is not a stub).

## Headline

Almost the entire assignment is blocked on ONE architectural feature: a faithful Why3 value
model for the **front-end IR node** — the nested `dict`/`list` "program_ir" with dynamic string
keys (`stmt`/`type` tags, `body`/`orelse`/`handlers`/`cases`, `symbol_table`, `contracts`, …).
Every `_check_*` / `_*_walk` / resolver / monomorphizer reflects on this structure via
`node.get("type")`, `isinstance(node, dict|list)`, recursion, and set-building. This is NOT a
bounded recognizer (the emit_ir ADT recognizer stack is for Module-6's *own* emit_ir nodes, a
different and far narrower shape); modeling the whole front-end IR is a real modeling feature =
hard-architectural. A second, smaller cluster is blocked on a **pure_ast AST-node value model**
(`ast.walk` + `isinstance`-on-AST + `NodeTransformer` visitor dispatch).

Secondary hard blockers layered on top (present in most of these bodies even if the node were
modeled): **nested-function closures** (`found=[False]; def walk(node): …` — the dominant pattern
in core_ir_semantic), **raising a typed exception with an f-string** (`raise PyCSLSemanticError(…)`),
`warnings.warn(...)`, `copy.deepcopy` IR reconstruction, and `defaultdict`.

## core_ir_semantic.py  (65 stubs)

Uniform verdict. All 65 are IR-tree checkers: take the IR `func`/`ir` dict, walk nested
dicts/lists, `.get(tag)`, raise `PyCSLSemanticError` / `warnings.warn`. **65/65 hard-architectural**,
all on the SAME feature (front-end-IR dict-node value model + nested-closure walk + raise-typed-exc).
0 trivial-leaf, 0 needs-recognizer, 0 floor.

| stub (family) | bucket | reason |
|---|---|---|
| run_ir_semantic_checks + all `_check_*` (span, no_exception, assigns_regions, contract_exprs, contract_scope, subscript_assignments, checkpoints, mutable_defaults, acts, ghost_string_ops, diverges, lemma, union_narrowing, noreturn, noreturn_successors, typeddict_access, namedtuple_access, callable_params, happy, mutex_invariants, class_invariants, concurrency, fresh_globals, union_gt1, final) | hard-architectural | walk the IR dict/list tree, `.get("type"/"stmt")`, raise typed exc |
| all `_*_walk` / `_*_stmt` / `_*_descend` / `_pb_*` / `_cs_*` / `_sa_*` / `_conc_*` / `_typeddict_*` / `_namedtuple_*` / `_union_*` / `_final_*` / `_hp_collect_written` / `_collect_call_targets` | hard-architectural | recursive IR-node reflection; several use nested-closure `walk` |
| `_ir_free_vars`, `_contains_result`, `_body_has_raise`/`_return`/`_diverging_construct`, `_lemma_returns_value`, `_lemma_calls_trusted`, `_collect_noreturn_names`, `_stmt_is_noreturn_call` | hard-architectural | IR-node predicate walkers (bool/set/str returns, but over the dict-node tree) |

Lightest members (still hard, but note for a *future* pickup once the func-IR record exists):
`_check_mutable_defaults` (reads one bool flag `func.get("has_mutable_default")` + raise) and
`_check_callable_params` (iterates the `symbol_table` str→str map, string `.partition("->")` /
`.split(",")` / `.isidentifier()` + raise) do NOT walk the deep tree — they'd fall out nearly
trivially the moment `func` is a modeled record with a `symbol_table: map string string` field.

## frontend/monomorphize.py  (24 stubs)

| stub | bucket | reason |
|---|---|---|
| apply_monomorphization | hard-architectural | orchestrator over ir_data dict; raises |
| _collect_generic_decls | hard-architectural | builds dict-of-dict over ir_data type_decls/functions |
| _check_gt3_schema_only | hard-architectural | iterate generics dict-of-record, raise |
| _collect_instantiations | hard-architectural | IR walk + symbol_table iteration |
| _find_subscript_calls | hard-architectural | IR statement walk |
| _scan_node_for_subscript_calls | hard-architectural | recursive IR-node scan |
| _type_str | hard-architectural | `node: Any` is str|dict union — needs IR-node model |
| _collect_instantiations_ast | hard-architectural | pure_ast AST walk + isinstance-on-AST |
| _extract_ast_subscript | hard-architectural | pure_ast AST Subscript/Name model |
| _check_gt4_polymorphic_recursion | hard-architectural | pure_ast AST walk |
| _check_bounds | hard-architectural | iterate generics dict-of-record, raise |
| _emit_specializations | hard-architectural | deepcopy IR construction + dict-of-record rewrite |
| _specialize_decl | hard-architectural | copy.deepcopy IR + field rewrite |
| _specialize_function | hard-architectural | copy.deepcopy IR + contract rewrite |
| _subst_type_in_ir | hard-architectural | recursive IR reconstruction |
| _rewrite_call_sites | hard-architectural | IR body rewrite |
| _rewrite_subscript_calls_in_stmt | hard-architectural | recursive IR rewrite |
| _rewrite_subscript_to_name | hard-architectural | recursive IR rewrite |
| _rewrite_annotations | hard-architectural | symbol_table rewrite |
| _record_classification | hard-architectural | ir_data dict mutation |
| _match_generic_annotation | needs-recognizer:regex (`re.match` w/ groups) | returns `(g,ct)` from a `re.match(r"...\[...\]")` — regex not modeled |
| _rewrite_annotation_str | needs-recognizer:regex (`re.match` w/ groups) | same regex shape |
| _mangled_name | needs-recognizer:regex (`re.sub`) | `re.sub(r"[^A-Za-z0-9_]","_",ct)` then f-string — string leak via unmodeled re.sub |
| _sanitize_type_name | needs-recognizer:str-in-literal-tuple membership + Optional[str] sentinel | pure string: `name in ("int",...)`, else return name; `return None` sentinel. Closest to trivial but for the tuple-membership + Optional |

Buckets: 20 hard-architectural, 4 needs-recognizer, 0 trivial-leaf, 0 floor.

## frontend/ir_resolve.py  (20 stubs)

Heavy multi-file import machinery: opens dependency source files, **re-runs Modules 1→5** on them,
probes the filesystem via `os.path`, deep-copies + mutates the IR, nested closures, `print`, BFS.

| stub | bucket | reason |
|---|---|---|
| _resolve_module_path | floor | `os.path.isfile/join/dirname/abspath` filesystem probing — external I/O boundary, irreducibly opaque |
| _get_module_exports | floor | `open(f)` + `_ast.parse` + walk — file I/O + parser boundary |
| _process_dependency | floor | `open` + `Module1_Ingestor/Parser/Weaver/Module5` + `json.loads` + recursion — re-invokes the whole toolchain |
| _collect_calls | hard-architectural | recursive IR-node walk → set |
| _rewrite_ir_calls | hard-architectural | recursive IR mutation |
| _strip_dir_scan_proofs | hard-architectural | list-of-dict `.get("proof")` filter, `str(...).startswith`, frozenset |
| _contract_referenced_var_names (×2 dup def) | hard-architectural | nested-closure `_walk` over IR contracts → set |
| _contract_referenced_names | hard-architectural | nested-closure `_walk` over IR contracts → set |
| _find_record_type_from_dep_imports | hard-architectural | cache dict + calls floor I/O fns |
| _inject_functions | hard-architectural | ir_data["functions"] list mutation + set |
| _resolve_direct_imports | hard-architectural | defaultdict, deepcopy, dict-of-record mutation, invokes floor fns, print |
| _resolve_wildcard_imports | hard-architectural | same shape |
| _resolve_module_imports | hard-architectural | same shape |
| _resolve_imported_classes | hard-architectural | same shape |
| _resolve_imported_base_classes | hard-architectural | same shape |
| apply_inheritance | hard-architectural | nested-closure `merge_one` recursion, deepcopy, dict-of-record |
| apply_composition | hard-architectural | nested closures, deepcopy, dict-of-record, raises |
| resolve_imports | hard-architectural | orchestrator over imports tuples, calls resolvers |
| resolve | hard-architectural | mutates module-global `_EXTRA_IMPORT_PATHS`, orchestration |

Buckets: 3 floor, 17 hard-architectural, 0 trivial-leaf, 0 needs-recognizer.
(The 5 `_resolve_*` resolvers + `_find_record_type_from_dep_imports` are floor-ADJACENT — they
transitively call the I/O boundary — but I keep them hard-architectural because they also do heavy
model-able IR dict mutation; they only become convertible once both the IR model AND a trusted
`val` boundary for the I/O leaves exist.)

## frontend/ir_inline.py  (11 stubs)

| stub | bucket | reason |
|---|---|---|
| _method_key | **trivial-leaf** | `return f"{cls.lower()}__{method}"` — all-string f-string + `.lower()`; **spot-checked, L3-tc ✓** |
| _walk_dicts | hard-architectural | generator yielding IR dict nodes (generators unsupported + IR-node model) |
| _touches_global | hard-architectural | IR walk, `.get("type")`, set membership |
| _global_call_target | hard-architectural | IR-node model + `str.partition(".")` |
| _method_edges | hard-architectural | IR walk + string ops → set |
| _recursive_methods | hard-architectural | dict-of-record, nested closure `reaches_self`, worklist reachability |
| _assigned_locals | hard-architectural | IR walk → set |
| _substitute | hard-architectural | recursive IR reconstruction + `copy.deepcopy` (the DEFER row) |
| _check_no_aliasing | hard-architectural | IR walk, raise |
| _inline_calls | hard-architectural | builds `_Inliner` object, loops |
| apply_inline_globals | hard-architectural | orchestrator, dict ops, calls stubs |

Buckets: 1 trivial-leaf, 10 hard-architectural, 0 needs-recognizer, 0 floor.

## frontend/exec_splice.py  (3 stubs)

| stub | bucket | reason |
|---|---|---|
| _is_constant_exec | hard-architectural | isinstance chain on AST Call/Name/Constant → bool (AST-node model) |
| _contains_exec | hard-architectural | `ast.walk` + isinstance-on-AST |
| splice_constant_exec | hard-architectural | instantiates a `NodeTransformer` subclass + `.visit(tree)` — visitor dispatch + AST transform |

Buckets: 3 hard-architectural. (`_ExecSplicer.visit_Expr` is a method, not a top-level stub.)

## frontend/module_collect.py  (3 stubs)

| stub | bucket | reason |
|---|---|---|
| _module_const_int | hard-architectural | `isinstance(value, ast.Constant/UnaryOp/USub)` on AST — AST-node value model |
| collect_module_constants | hard-architectural | iterate `node.body`, isinstance-on-AST, `ast.walk`, dict/set build |
| collect_module_globals | hard-architectural | same shape (ast.walk + isinstance) |

Buckets: 3 hard-architectural. (`collect_module_const_dicts` is a newer LIVE fn absent from the
mirror — not a stub yet.)

## frontend/__init__.py  (0 stubs)

Pure package `import`/`__all__` re-exports (no annotated functions). Nothing to convert.

---

# Per-bucket totals (this group, 126 stubs)

| bucket | count |
|---|---|
| trivial-leaf (batch-convertible NOW) | **1** |
| needs-recognizer | 4 |
| hard-architectural | 118 |
| floor | 3 |

# Feature fan-out (top rows)

| feature (missing capability) | #stubs | example stubs |
|---|---|---|
| **front-end-IR dict-node value model** (nested dict/list program_ir; dynamic tag keys; + nested-closure walk + raise-typed-exception as co-requisites) | **~106** | all 65 core_ir_semantic; ir_resolve _collect_calls/apply_inheritance/apply_composition; ir_inline _touches_global/_substitute; monomorphize _collect_generic_decls/_emit_specializations |
| **pure_ast AST-node value model** (`ast.walk` + isinstance-on-AST + `NodeTransformer` visitor) | ~9 | module_collect (3), exec_splice (3), monomorphize _collect_instantiations_ast/_extract_ast_subscript/_check_gt4 |
| external filesystem / parser I/O boundary (floor `val`) | 3 | _resolve_module_path, _get_module_exports, _process_dependency |
| faithful regex `re.match`/`re.sub` (string) | 3 | _match_generic_annotation, _mangled_name, _rewrite_annotation_str |
| str `in (literal-tuple)` membership + Optional[str] sentinel | 1 | _sanitize_type_name |

Co-requisite sub-features folded into the top row (each is itself a hard modeling feature, not a
recognizer): nested-function closures (`def walk(node)` inside a body — pervasive in
core_ir_semantic), `copy.deepcopy` IR reconstruction (ir_inline `_substitute`; monomorphize
`_specialize_*`; ir_resolve `apply_inheritance`/`apply_composition`), `raise PyCSLSemanticError(f"…")`,
and `warnings.warn(...)`.

# Bottom line for the orchestrator

- **1 cheap win now**: `ir_inline._method_key` (trivial-leaf, spot-checked green). It is the ONLY
  batch-convertible stub in this entire 126-stub group.
- The group is ~94% (118/126) hard-architectural, and ~106 of those collapse to a SINGLE feature —
  the front-end IR node value model. That feature is the highest-leverage unlock in this frontier
  BUT it is a genuine modeling feature (comparable in scope to the emit_ir ADT), not a bounded
  recognizer; and even with it, the nested-closure/deepcopy/raise co-requisites gate most bodies.
  Recommend treating this whole group as **deferred behind the IR-node-model feature**, converting
  only `_method_key` opportunistically.
- 3 floor stubs (ir_resolve I/O) are irreducible: they open files and re-invoke Modules 1→5 — a
  trusted `val` boundary, never a body-verified port.

# Uncertainty notes
- `_sanitize_type_name`: borderline trivial-leaf vs needs-recognizer. Classified needs-recognizer
  because `name in ("int","bool",...)` (str-in-tuple membership) and the `Optional[str]`/`return None`
  sentinel are two small features I did not spot-check. If str-in-literal-tuple already lowers as
  chained equality, it collapses to trivial-leaf after an `Optional[str]→str` sentinel sweep.
- The 5 `_resolve_*` resolvers are floor-adjacent (call the I/O boundary); kept hard-architectural
  rather than floor because their own bodies are model-able IR mutation.
