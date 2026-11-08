# Triage-A6 — Module6 helpers + Transpiler (186 `\trusted` stubs)

READ-ONLY static triage. Buckets: trivial-leaf / needs-recognizer:<F> / hard-architectural / floor.
Classified against the LIVE bodies in `src/pycsl/…`; mirror placeholders in `src/self-annotate/src/…`.

Dominant finding: this group is overwhelmingly the **expression/statement emitter core** — the
`_handle_*_expr` handlers and stmt/expr lowering recurse through `self._e` / `self._stmts_to_whyml`
over IR nodes and reflect on non-standard emit_ir sub-node fields (`node.dict/.key/.set/.head/.tail/
.list/.left/.right/.lo/.hi/.elts/.tuple/.string/.arr`). Per the recognizer rubric these are the
"emit_ir ADT has no <K> arm — DEFER/blocked" architectural gaps (the SEMANTIC CEILING on body-faithful
`_handle_*`). They are NOT one-recognizer fixes.

---

## module6_whyml/expr_ghost_collections.py  (24 stubs)  [classified directly]

| stub | bucket | missing feature / reason |
|---|---|---|
| _handle_map_empty_expr | trivial-leaf | returns constant string `"(const (None: option int))"`; no node reflection, no `self._e` |
| _handle_set_empty_expr | trivial-leaf | returns constant `"(const false)"` |
| _handle_nil_expr | trivial-leaf | returns constant `"Nil"` |
| _handle_map_get/set/eq/remove, _handle_has_key (5) | hard-architectural | reflect `node.dict/.key/.value/.left/.right` sub-node fields + recurse via `self._e`/`self._deref`; emit_ir ADT has no Map-node arms |
| _handle_set_add/remove/mem/union/inter/diff/card/subset/eq (9) | hard-architectural | reflect `node.set/.elem/.left/.right/.lo/.hi` + `node.kind` dispatch + recurse `self._e`; emit_ir ADT has no Set-node arms |
| _handle_cons/hd/tl/list_length/nth/mem/append (7) | hard-architectural | reflect `node.head/.tail/.list/.index/.elem/.left/.right` + recurse `self._e`/`self._deref`; emit_ir ADT has no List/Cons-node arms |

Counts: trivial-leaf=3, needs-recognizer=0, hard-architectural=21, floor=0.

## module6_whyml/expr_ghost_spec_ops.py  (12 stubs)  [classified directly]

| stub | bucket | missing feature / reason |
|---|---|---|
| _handle_mktuple_expr | hard-architectural | generator over `node.elts` node-LIST + `str.join`, recurse `self._e`; needs emit_ir node-list arm |
| _handle_fst_expr / _handle_snd_expr | hard-architectural | `node.tuple` sub-node + `self._e` + `.lstrip("!")`/`.startswith` + let-binding string build |
| _handle_proj_expr | hard-architectural | `node.tuple.to_dict().get("name")`, `self._ghost_tuple_vars.get`, `["_"]*arity` list-mult + join |
| _handle_ctor_test_expr / _handle_ctor_payload_expr | hard-architectural | `getattr(self,"_constructors",{}).get(...).get(...)`, list-index payload, arity dispatch |
| _handle_strconcat / _handle_str_length / _handle_str_sub (3) | hard-architectural | `node.left/.right/.string.to_dict()` sub-node + `self._expr_to_whyml_string_ctx` recurse |
| _handle_ghost_copy / _handle_ghost_copy_range / _handle_ghost_make (3) | hard-architectural | `node.arr/.size/.default/.lo/.hi` sub-node + `self._e` recurse; Array.copy/sub/make forms |

Counts: trivial-leaf=0, needs-recognizer=0, hard-architectural=12, floor=0.

## module6_whyml/identifiers.py  (2 stubs)  [classified directly]

| stub | bucket | missing feature / reason |
|---|---|---|
| stable_hash | floor | body is `int(hashlib.sha256(s.encode()).hexdigest()[:8],16) % N` — irreducibly opaque external crypto (hashlib); no faithful model, abstract-val/floor boundary |
| whyml_ident | hard-architectural | `unicodedata.normalize('NFD',ch)` external + per-char `ord()>127` decomposition loop building a list + set membership + `.isupper()/.lower()`; external-lib call |

Counts: trivial-leaf=0, needs-recognizer=0, hard-architectural=1, floor=1.

## module6_whyml/preamble.py  (25 stubs)  [PreambleEmissionMixin]

Counts: trivial-leaf=0, needs-recognizer=4, hard-architectural=21, floor=0.
needs-recognizer: `_inductive_sig_whyml` (List[str] .append + `" ".join` builder — best single pickup,
pure string, no IR/self/recursion), `_mutex_inv_params` (sorted str-list-comp + substring `x in s`),
`_mutex_inv_application` (str `.join` over comprehension), `_emit_opaque_class_aliases` (List[str]-param
in-place `.append` mutation + func-IR reflection).
The other 21 are hard-architectural: nested recursive closures walking generic IR dicts (`nonlocal`
sentinels), pervasive `Set[str]` locals/returns (rubric DEFER), heterogeneous-value `needs` dict needing
a record model, `str.split()` decl-parsing, recursive IR deep-copy (`_subst_self_in_expr`, `_emit_type_decls`
— §5 gap #4), and aggregators calling the giant trusted `_expr_to_whyml`/`_subst_self_in_expr` siblings
(ordering). FILE-LEVEL prereq: the mirror class is a PLAIN class; every self-field read (`self.ir`,
`self._record_types`, …) leaks to opaque until the mirror is made `@mutable_state @dataclass` with fields
declared — a per-FILE gate blocking essentially all 25.
Fan-out (this file): str-list `.append` builder ~18 · Set-valued locals ~10 · nested recursive IR-walk
closure ~8 · heterogeneous needs-dict→record 4 · calls giant trusted sibling (ordering) ~6.

## module6_whyml/stmt_control_flow.py  (22 stubs found; brief said 23)  [ControlFlowStmtMixin — IS @mutable_state]

Counts: trivial-leaf=6, needs-recognizer=4, hard-architectural=12, floor=0.
trivial-leaf: `_materialize_bridge`, `_materialize_str_bridge`, `_bool_ir_to_int_wrap`, `_coerce_to_int`
(uncertain: uses `stable_hash`), `_try_local_decl_kind`, `_union_arm_whyml_type` (landed local-dict-value
recognizer). NOTE: 4 of these physically LIVE in sibling modules (statements.py/types.py/expressions.py) —
converting them in THIS mirror is a duplicate verified body; the real leaf is the home file.
needs-recognizer: `_seq_init_expr` (`reversed()` iter), `_to_bool` (`_is_string_expr`/emit_ir dep),
`_pattern_has_constructor` (`any()`-over-gen + pattern-dict reflection), `_infer_return_value_type`
(`Optional[str]` sentinel).
hard-architectural (12): `_expr_to_whyml` + `_stmts_to_whyml` = the CORE giant IR/stmt dispatchers
(mutual recursion over every node type); `_classify_iterable`, `_first_assign_value_ir` (returns IR node),
`_callee_raised_direct/_in` (Set-valued + recursive closure), and the match/union family
(`_try_union_is_none_match`, `_match_pattern_cond`, `_render_match_pattern`, `_match_subject_union_info`,
`_union_ctor_for_arm_tag`, `_maybe_inject_union_return`) = variant/match dispatch + IR value model.

## module6_whyml/types.py  (18 stubs)  [TypeInferenceMixin — PLAIN class, §7 record prereq applies]

Counts: trivial-leaf=2, needs-recognizer=8, hard-architectural=8, floor=0.
trivial-leaf: `_val_is_bool` (uncertain: const-frozenset membership), `_bool_ir_to_int_wrap`.
needs-recognizer=8: SEVEN of these are gated behind the SAME per-FILE prerequisite — making the mirror
`TypeInferenceMixin` a `@mutable_state @dataclass` with its `_record_types`/`_ghost_*_vars`/`_array_locals`/
`_dict_locals` fields declared, so self-field `.get`/membership stops leaking to opaque `contains_check`:
`_first_assign_kind`, `_rhs_yields_array`, `_rhs_yields_map`, `_resolve_effective_ghost_type`,
`_field_type_for`, `_field_type_of`, `_call_return_whyml_type` (+ `str.rpartition`); plus `_split_tuple_type`
(faithful `str.split`→array string; uncertain — may already be trivial via landed string ops, NO self-field).
hard-architectural=8: `_track_collection_metadata`, and the `_collect_*_var_assigns` / `_collect_struct_*`
family — all Set-valued or Dict-returning fixpoint scanners with recursion + IR reflection (Set-local DEFER).

**HIGHEST SINGLE LEVER in this cluster: convert `TypeInferenceMixin` to a `@mutable_state @dataclass`
record — one per-file change flips 7 types.py needs-recognizer stubs toward convertible at once.**

## Module6_WhyMLTranspiler.py  (20 live stubs; `_emit_funcs`/`_symbol` are nested defs)

Counts: trivial-leaf=1, needs-recognizer=3, hard-architectural=16, floor=0.
trivial-leaf: `_wrap_unannotated_call_with_strict_assert` (uncertain — needs `_current_no_exception` field).
needs-recognizer: `_heap_var` (self-str-field-eq + raise), `_reset_module_accumulators` (empty-collection
field reset once class is a record), `_sig_val_from_let` (`str.replace(a,b,1)` + str-list build).
hard-architectural (16): `__init__` (json.loads + ~80 self-field record decls), the orchestration giants
(`transpile`, `_transpile_modular`, `_compute_shared_module_maps`, `_emit_prefunctions_infra`,
`_shared_use_lines`) that call dozens of still-trusted siblings (ordering), nested closures
(`_emit_funcs`, `_symbol`, `_collect_shared_symbol_decls`), set-valued/getattr/try-except/`template.format`
(`_callee_implicit_exceptions`, `_maybe_emit_no_exception_assert`, `_render_callee_condition`).

## module6_whyml/auto_trust.py  (12 stubs)

Counts: trivial-leaf=0, needs-recognizer=3, hard-architectural=9, floor=0.
needs-recognizer: `_build_witness_str` (str.join-over-list + int-interp), `_should_auto_trust_map_return`
(dict.get str-in-tuple membership; near-trivial), `_should_auto_trust_array_return` (external
`IRScanner.has_*` bool call; uncertain).
hard-architectural: `_check_witness_vals` = dynamic **`eval(test_expr)`** (item-3 ceiling); `_is_linear_expr`
+ `_test_contains_map` + `_has_set_op_on_map` = recursive nested-closure IR-dict walks;
`_collect_map_typed_locals`/`_should_auto_trust_tuple_return` = Set-valued + recursion; `_extract_array_lengths`
nested closures + self-slice; `_is_linear_vc`/`_should_auto_trust_set_op` = ordering on hard siblings.

## module6_whyml/struct_format.py  (4 stubs)  [MIRROR DRIFT — stale skeleton]

Counts: trivial-leaf=0, needs-recognizer=1, hard-architectural=3, floor=0.
Mirror is missing live `faithful_slots`/`faithful_tag`/`faithful_bytes_slot`/`_scalar_range` — re-sync the
class surface before touching stubs. `arity` = needs-recognizer (@dataclass tuple-field + `len()`; uncertain).
`slot_id` (RLE loop + str(int) + join), `parse_format`/`calcsize` (**regex** `_TOKEN_RE.match/.group` +
record construction) = hard-architectural.

## module6_whyml/scc.py  (5 stubs)

Counts: trivial-leaf=0, needs-recognizer=1, hard-architectural=4, floor=0.
`emits_as_logic_symbol` = needs-recognizer (generic dict.get→bool; uncertain, near-trivial). The rest are
Set-valued IR recursion (`find_calls_in_ir`, `find_self_method_calls`), Tarjan SCC (`compute_sccs` — nested
recursive closure + dict/list mutation), and the `sort_functions_by_scc` orchestrator.

## module6_whyml/abstract_ops.py  (4 stubs)

Counts: trivial-leaf=0, needs-recognizer=0, hard-architectural=4, floor=0.
All 4 mutate self dict-fields on a PLAIN (non-@mutable_state) `AbstractOpsMixin` class (§7 record prereq) +
`decl.split()`/`.count()` parsing, `getattr` dynamic, nested closures, `out.insert()`.

## module6_whyml/ir_scanner.py  (34 stubs)  [EMPIRICAL — sub-probe ran --no-proof type-checks per stub]

Counts: trivial-leaf=19, needs-recognizer=9, hard-architectural=6, floor=0.  **BIGGEST WIN SOURCE.**
trivial-leaf=19 (batch-convertible NOW, emitter-inert STUB ports, byte-diff trivially 0): the bool IR-tree
walkers `uses_arrayset, ends_with_return, has_continue, uses_continue, uses_break, has_direct_return,
has_in_loop_return, uses_for, uses_subscript, uses_array_lit, uses_minmax, is_recursive, uses_string,
uses_sum, uses_set_card, uses_ord_chr, uses_divmod, uses_inline_set_or_dict_ops` + `find_ghost_vars`
(simple set-local: `set()`+`.add`+`.update`+return Set — WORKS today).
KEY EMPIRICAL CORRECTION: generic IR-dict recursion (`stmt["body"]`, `.values()`), nested `def` helpers,
and simple set-locals ALL type-check today — the "recursion over IR = hard" heuristic is over-pessimistic
for scanner-style bool/set functions.
needs-recognizer=9: `|=` set-union aug-assign (5: `collection_binder_kinds, find_lambda_vars,
find_record_vars, find_append_targets, collect_user_exceptions` — rewritable to already-supported
`.update()`), nested value sub-node projection `stmt.get("value",{}).get(...)` (4, overlapping), plus
`uses_ghost_type` (set-PARAM membership), `has_early_return` (enumerate+len index-arith),
`find_return_type` (`str.join` over `["x"]*n`), `find_record_var_classes` (Dict[str,str]-local).
hard-architectural=6: `find_named_expr_targets`, `_collect_mutations` (caller-visible set/list PARAM
mutation-by-ref — genuine out-of-scope frame boundary) + their dependents `find_assigned_vars`,
`find_iteration_mutations`; `collect_escaping_exceptions` (external `exception_model.handler_catches`);
`find_array_and_dict_vars` (Tuple[Set,Set] + ≥2 deep features).

---

# GROUP TOTALS (182 stubs classified; brief's 186 differs by 4: stmt_control_flow 22 not 23,
# Transpiler 20 live stubs not 22 [2 nested defs], struct_format 4 not 5 [mirror drift])

| bucket | count |
|---|---|
| trivial-leaf (batch-convertible now) | **31** |
| needs-recognizer | **33** |
| hard-architectural | **117** |
| floor | **1** (identifiers.stable_hash — hashlib.sha256 opaque) |

Per-file trivial-leaf: ir_scanner 19 · stmt_control_flow 6 · expr_ghost_collections 3 · types 2 ·
Transpiler 1 · (all others 0).

## TOP feature fan-out (whole group) — near-term recognizer wins first, then architectural blockers

| feature / blocker | ~#stubs | example stubs | kind |
|---|---|---|---|
| IR-node/emit_ir ADT value model + sub-node projection (spot-check-confirmed: `unbound type emit_ir`) | ~45 | all 33 `_handle_*_expr`, `_expr_to_whyml`, `_stmts_to_whyml`, `_first_assign_value_ir` | hard |
| Set-valued return / fixpoint scanner (rubric DEFER) | ~25 | `_collect_*_var_assigns`, `find_calls_in_ir`, `_callee_raised_*`, `_scan_preamble_needs` | hard |
| str-list `.append`/`+=` builder + return List[str] | ~18 | preamble `_emit_*`, `_inductive_sig_whyml` | hard/near |
| nested recursive closure walking generic IR (+nonlocal) | ~14 | `_func_returns_string_seq`, `_is_linear_expr`, `compute_sccs`, `_extract_array_lengths` | hard (but simple keyed walkers proven OK in ir_scanner) |
| orchestrator ordering (calls still-trusted siblings) | ~13 | `transpile`, `_transpile_modular`, `_emit_preamble`, `sort_functions_by_scc` | hard (ordering) |
| **types.py `TypeInferenceMixin`→@mutable_state @dataclass record prereq** | 7 | `_resolve_effective_ghost_type`, `_first_assign_kind`, `_field_type_for` … | needs-recognizer (ONE per-file change flips 7) |
| `\|=` set-union aug-assign (→ rewrite `.update()`) | 5 | `collection_binder_kinds`, `find_lambda_vars`, `collect_user_exceptions` | needs-recognizer |
| caller-visible set/list PARAM mutation-by-ref | ~5 | `find_named_expr_targets`, `_collect_mutations`, `_emit_opaque_class_aliases` | hard (frame boundary) |
| nested value sub-node projection `.get("value",{}).get(...)` | 4 | `find_lambda_vars`, `find_record_vars`, `find_append_targets` | needs-recognizer |
| `Optional[str]` return sentinel sweep | 4 | `_infer_return_value_type`, `_field_type_for`, `_call_return_whyml_type` | needs-recognizer |
| dynamic `eval`/`getattr`/`try-except`/regex (item-3 ceiling / opaque) | ~6 | `_check_witness_vals` (eval), `_maybe_emit_no_exception_assert` (getattr), `parse_format`/`calcsize` (regex) | hard/floor-ish |

## Batch-convertible-NOW shortlist (the 31 trivial-leaf) — highest priority
- **ir_scanner: 19** bool/set IR-tree scanners (empirically type-checked). This one file is the cheap-win
  motherlode; convert as a batch (STUB ports, byte-diff 0).
- stmt_control_flow: 6 (`_materialize_bridge`, `_materialize_str_bridge`, `_bool_ir_to_int_wrap`,
  `_coerce_to_int`*, `_try_local_decl_kind`, `_union_arm_whyml_type`) — NOTE 4 physically live in sibling
  modules (dup body here; real leaf is home file).
- expr_ghost_collections: 3 constant-string handlers (`_handle_map_empty_expr`, `_handle_set_empty_expr`,
  `_handle_nil_expr`).
- types: 2 (`_val_is_bool`*, `_bool_ir_to_int_wrap`). Transpiler: 1 (`_wrap_unannotated_call_with_strict_assert`*).
  (* = flagged uncertain by the sub-probe; spot-check before batching.)

## Best SINGLE structural lever
Convert `types.py TypeInferenceMixin` (and similarly `PreambleEmissionMixin`, `AbstractOpsMixin`) to a
`@mutable_state @dataclass` record: a per-FILE change that unblocks 7 types.py needs-recognizer stubs at
once and de-opaques self-field access across those files.

## Caveats
- The two `_handle_*_expr` files (36 stubs, classified STATICALLY then spot-check-validated on one rep):
  confirmed hard — the typed `ExprIR` param lowers to `unbound type emit_ir` standalone; they need the
  emit_ir ADT + sub-node arms wired in. Not near-term.
- ir_scanner verdicts are `--no-proof` type-check only (discharge of `ensures True` expected trivial but
  full proof not run, per read-only budget).
- struct_format mirror is a STALE skeleton (missing `faithful_slots`/`faithful_tag`/`faithful_bytes_slot`/
  `_scalar_range`) — re-sync class surface before touching its stubs.
- floor is essentially empty (1): almost nothing here is irreducible — the trusted mass is emitter
  machinery gated behind ~4 big reusable features (IR-node value model, set-valued returns, str-list
  builder, record-ify mixins), not per-leaf axioms.
