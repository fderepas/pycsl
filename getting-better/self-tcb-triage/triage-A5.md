# Triage A5 — Module6 WhyML emitter CORE (`_handle_*`/`_emit_*` handlers)

Scope: `module6_whyml/{expressions.py (53), statements.py (43), functions.py (36)}` = 132 `\trusted` stubs.
READ-ONLY. Classification is static (recognizer stack + self-tcb §8 recorded verdicts) plus 2 `--no-proof`
spot-checks on the only ambiguous trivial-leaf hopes. No conversions, no commits.

## Headline
This is the **highest-soundness-value but hardest** T1 territory, and it is almost entirely
**feature-gated** — consistent with self-tcb §8 iters 16–23 ("in-stack-recognizer / byte-diff-0 STUB-port
frontier is EXHAUSTED; every remaining leaf needs a demand-driven emitter FEATURE"). Only **1 confirmed
trivial-leaf** (`_symtype_to_whyml`, spot-check L3-tc ✓). The rest split into a handful of single-feature
`needs-recognizer` leaves and a large `hard-architectural` core (the IR-dispatch keystones + everything
transitively blocked on them).

Two spot-checks run (port live body → `--no-proof` → revert):
- `functions._symtype_to_whyml` → **L3-tc ✓** (pure `str in (tuple)` → string-literal returns; same shape
  as the already-converted `_union_arm_whyml_type`). Genuine trivial-leaf. Only a benign C8 Union warning
  on the `Optional[str]` param (not a leak).
- `statements._wrap_body_with_return_catch` → confirmed **hard** via the mirror's own inline blocker
  comment: mixed-literal f-strings (`f"    try\n{body_code}\n..."`) hash literal segments to **int** →
  `str_concat` int/string leak. This is the pervasive **F-fstring** blocker.

## The dominant blocker taxonomy (named features)
| tag | feature that would unblock it | character |
|---|---|---|
| **F-irdispatch** | the central multi-way IR-node dispatchers themselves (`ir.get("type")`/`stmt` → 300+-line handlers) | hard-arch keystone |
| **F-dispatcher** | leaf calls still-`\trusted` `_expr_to_whyml`/`_stmts_to_whyml` (return string, modeled `int` → leak); ordering-blocked on the keystone | hard-arch (ordering) |
| **F-fstring** | faithful **mixed-literal f-string** concat (literal segment currently hashes to int) — pervasive across every string-builder | recognizer (big fan-out) |
| **F-mapbuild** | build a `Dict[str,…]`/nested-map **over an IR function/method list** (the `_build_method_*_map` family) | modeling |
| **F-set** | set-local declaration/mutation (`Set[T]` return, `x.add()/discard()`) — §5 gap#2, still absent | modeling |
| **F-irrec** | recursive IR **traversal/construction** (worklist / nested closure / deep-copy) — §5 gap#4 | modeling |
| **F-binop** | BinOp-operand projection `ir.get("left")/("right")` — §5 gap#3 (emit_ir ADT has no BinOp arm) | recognizer(blocked) |
| **str.startswith** | faithful `str.startswith/endswith(prefix)` recognizer (the coerce-helper family) | recognizer |
| **F-strops** | compound string parsing `rsplit/partition/split/join` | recognizer |
| **F-nesteddict** | nested-dict string-value projection `record_types[t]["whyml_name"]` (field_get's iter-19 feature, plain-mixin generalization) | modeling |
| **F-eltval** | emit_ir element value projection `elts[0].get("value")` | recognizer |
| **F-ord** | `ord(c)`/char-sum loop modeling | modeling |

---

## expressions.py (53 stubs)

| stub | bucket | missing feature / reason |
|---|---|---|
| `_expr_to_whyml` (358L) | hard-architectural | **F-irdispatch — THE expression keystone**; every leaf below transitively waits on it |
| `_handle_binop` (322L), `_handle_call_expr` (312L), `_call_named_builtins` (423L), `_handle_subscript` (374L), `_is_string_expr` (221L), `_emit_membership` (170L), `_handle_attribute_expr` (116L), `_resolve_dotted_signature`, `_handle_dotted_call`, `_handle_len_call`, `_content_string_method`, `_handle_struct_call`, `_match_field_decode_idiom` | hard-architectural | F-irdispatch — deep multi-way IR-node reflection (recorded hard in §8 iter-16 for binop/call/subscript/attribute) |
| `_e`, `_iter_len_expr`, `_match_pattern_cond`, `_dv_store_value`, `_emit_bitwise_or_power`, `_handle_join_call`, `_dotted_ensures_suffix`, `_recognize_field_decode_idiom`, `_content_string_method`, `_typeddict_field_access`, `_typeddict_record_literal`, `_namedtuple_positional_access`, `_call_record_constructor`, `_call_bytes_methods`, `_expr_to_whyml_string_ctx`, `_seq`/coerce callers | hard-architectural | F-dispatcher — calls still-`\trusted` `_expr_to_whyml` (string→int leak) and/or F-fstring |
| `_emit_contract_logic_symbol`, `_handle_isinstance`, `_str_operand_to_int` | hard-architectural | F-fstring string-building + `_add_abstract_op` |
| `_subst_params`, `_frame_trigger_term` | hard-architectural | F-irrec — recursive IR deep-copy / node-value recursion (§5 gap#4) |
| `_linear_form`, `_static_width`, `_is_float_expr` | needs-recognizer:F-binop | BinOp-operand projection absent (§5 gap#3, recorded) |
| `_union_none_ctor_for` | hard-architectural | F-nesteddict — iterates `_variant_types[…]["constructors"]` nested dict |
| `_tag_of_value` | needs-recognizer:F-ord | `sum(ord(c) for c in name)` char loop |
| `_is_null_byte_lit` | needs-recognizer:F-eltval | `elts[0].get("value")==0` emit_ir element-value projection |
| `_coerce_str_arg`, `_coerce_to_int`, `_array_coerce_arg`, `_coerce_dotted_args`, `_str_operand_to_int` | needs-recognizer:str.startswith | `whyml_str.startswith(prefix)` prefix-classifier + `stable_hash` (opaque int) |
| `_module_binding_names`, `_push_quant_binder`, `_pop_quant_binder`, `_add_abstract_op` | needs-recognizer:F-set | Set return / set-field mutation (§5 gap#2, recorded blocked) |
| `_emit_metatype_tags` | uncertain (→needs-recognizer:abstract-op-writes-frame) | only calls `_add_abstract_op` with fixed literal strings; would convert iff the sibling stub's `writes {self._abstract_ops}` frame is honored — marginal |
| `_is_emit_ir_expr` (84L), `_to_bool` (126L) | hard-architectural | F-irdispatch reflection |

**expressions counts:** trivial-leaf 0 · needs-recognizer 13 · hard-architectural 40 · floor 0

## statements.py (43 stubs)

~21 stubs are **cross-file duplicate sibling stubs** (the mirror re-declares `ExpressionEmissionMixin`
helpers so `statements.py` type-checks standalone — see the inline `_add_abstract_op` comment). Their
verdict = their home (expressions.py) verdict; they are not independent conversion targets.

| stub | bucket | missing feature / reason |
|---|---|---|
| `_stmts_to_whyml` (112L) | hard-architectural | **F-irdispatch — THE statement keystone** |
| `_emit_body_code` (188L), `_typed_local_vars` (152L) | hard-architectural | F-irdispatch + F-set (set locals) |
| `_emit_first_assign`, `_emit_new_ghost_ref`, `_emit_array_local_reassign`, `_seq_init_expr`, `_seq_operand`, `_emit_frame_condition` | hard-architectural | F-dispatcher (calls `_stmts_to_whyml`/`_expr_to_whyml`) + F-set / F-fstring |
| `_wrap_body_with_return_catch` | needs-recognizer:F-fstring | **spot-check + mirror comment CONFIRM**: mixed-literal f-string → int-hash leak; the single cleanest F-fstring example |
| `_collect_string_elem_read_locals`, `_collect_field_decode_str_locals` (+ their nested `rec`) | needs-recognizer:F-set (rec: hard/F-irrec) | Set-valued collectors; nested `rec` closures recurse IR |
| `_call_returns_string_collection` | needs-recognizer:str.startswith | `.startswith("IRScanner.…")` + calls trusted `_resolve_dotted_signature` (ordering) |
| 21× duplicate siblings (`_expr_to_whyml`,`_is_string_expr`,`_resolve_dotted_signature`,`_handle_return_stmt`,`_field_type_of`,`_resolve_effective_ghost_type`,`_mutex_inv_application`, `_coerce_to_int`,`_array_coerce_arg`,`_str_operand_to_int`,`_add_abstract_op`,`_e`,`_dv_store_value`, …) | hard-architectural (mostly) / needs-recognizer:str.startswith\|F-set (the coerce/set ones) | inherit home-file verdict; blocked on home-file conversion |

**statements counts:** trivial-leaf 0 · needs-recognizer ~8 · hard-architectural ~35 · floor 0
(≈21 of the hard bucket are duplicate sibling stubs, not new targets.)

## functions.py (36 stubs)

| stub | bucket | missing feature / reason |
|---|---|---|
| `_symtype_to_whyml` | **trivial-leaf** | **spot-check L3-tc ✓** — `symtype in (tuple)` → string-literal returns; same shape as the already-converted `_union_arm_whyml_type`. Batch-convertible NOW. |
| `_build_method_return_annotation_map` (15L), `_build_method_writes_map` (17L) | needs-recognizer:F-mapbuild | simplest of the map family: iterate IR functions → `Dict[str,str]`/`Dict[str,List[str]]`; needs string-map construction over an IR list |
| `_build_method_return_type_map`, `_build_method_result_ensures_map`, `_build_method_param_result_ensures_map` (85L), `_build_method_field_result_ensures_map` (82L), `_build_method_field_param_result_ensures_map` (106L), `_build_method_field_old_ensures_map`, `_build_method_field_param_post_ensures_map` (94L), `_build_method_field_param_frame_ensures_map` (110L), `_build_method_result_frame_ensures_map` (105L), `_build_method_param_types_map`, `_build_method_param_whyml_types_by_name` | hard-architectural | F-mapbuild over **deep contract/ensures** IR reflection + nested `Dict[str,List[…]]` construction |
| `_collect_record_fields` | needs-recognizer:F-set | `Set[str]` return |
| `_callable_tag_to_whyml` | needs-recognizer:F-nesteddict | `record_types[tag]["whyml_name"]` nested-dict projection (else str-in-tuple, close) |
| `_callable_whyml_arrow`, `_parse_mixin_sig` | needs-recognizer:F-strops | `partition/split/join` / `rsplit` string parsing + list build |
| `_emit_function` (226L), `_param_type_str` (108L), `_reset_function_state` (160L), `_emit_contracts` (101L), `_build_param_list`, `_infer_tuple_slot_type`, `_refine_tuple_return_type`, `_compute_return_type`, `_emit_narrowing_vc`, `_emit_union_arm_vc`, `_render_refinement_goal`, `_emit_subtyping_goals`, `_mixin_dep_pseudo_functions`, `_compute_scope_sets` | hard-architectural | F-irdispatch / F-set / F-fstring (the emit keystones) |
| `_has_dynamic_exec`, `_collect_assign_targets`, `_returns_string_seq`, `_first_tuple_return_elts` | hard-architectural | F-irrec — worklist / nested-closure IR recursion (returns bool or emit_ir list) |

**functions counts:** trivial-leaf 1 · needs-recognizer 6 · hard-architectural 29 · floor 0

---

## Per-bucket counts (A5 group, 132)
| bucket | count |
|---|---:|
| trivial-leaf (batch-convertible now) | **1** |
| needs-recognizer (one named feature) | **27** |
| hard-architectural | **104** |
| floor | 0 |

## Feature fan-out (primary blocker per stub; top rows)
| feature | #stubs | example stubs |
|---|---:|---|
| **F-irdispatch / F-dispatcher** (central dispatch keystones + everything blocked on `_expr_to_whyml`/`_stmts_to_whyml`) | ~55 | `_expr_to_whyml`, `_stmts_to_whyml`, `_handle_binop`, `_handle_call_expr`, `_handle_subscript`, `_e`, `_seq_operand` |
| **F-mapbuild** (dict/nested-map over IR method list) | ~13 | `_build_method_*_map` family, `_build_method_return_annotation_map` |
| **F-set** (set-local modeling — §5 gap#2) | ~11 | `_module_binding_names`, `_collect_*_locals`, `_collect_record_fields`, `_push/_pop_quant_binder` |
| **F-fstring** (mixed-literal f-string → int-hash) — as sole/primary blocker | ~9 | `_wrap_body_with_return_catch`, `_emit_contract_logic_symbol`, `_str_operand_to_int` (also a SECONDARY blocker on 40+ string-builders) |
| **F-irrec** (recursive IR traversal/construction — §5 gap#4) | ~8 | `_subst_params`, `_has_dynamic_exec`, `_frame_trigger_term`, `_returns_string_seq`, `_first_tuple_return_elts` |
| **str.startswith/endswith** recognizer | ~7 | `_coerce_to_int`, `_coerce_str_arg`, `_array_coerce_arg`, `_call_returns_string_collection` |
| **F-binop** (BinOp-operand projection — §5 gap#3) | 3 | `_linear_form`, `_static_width`, `_is_float_expr` |
| **F-strops** (partition/split/rsplit/join) | 2 | `_callable_whyml_arrow`, `_parse_mixin_sig` |
| F-nesteddict / F-eltval / F-ord | 1 each | `_callable_tag_to_whyml` / `_is_null_byte_lit` / `_tag_of_value` |

## Trivial-leaf count (batch-convertible now): **1** — `functions._symtype_to_whyml` (spot-check L3-tc ✓).

## Recommendations for the coordinator
1. **Cheapest concrete win now:** convert `_symtype_to_whyml` (trivial-leaf, verified type-check).
2. **Highest-leverage recognizer:** **F-fstring** (faithful mixed-literal f-string concat). It is a
   SECONDARY blocker on essentially every string-building emitter in this territory (40+ stubs); landing
   it collapses a whole layer once the dispatcher blocker is also cleared. `_wrap_body_with_return_catch`
   is its cleanest driver.
3. **Next single-feature recognizers (small fan-out but real):** str.startswith (7), F-binop (3, unblocks
   `_is_float_expr`/`_linear_form`), F-strops (2).
4. **The 104-stub hard core is dominated by two IR-dispatch keystones** (`_expr_to_whyml`,
   `_stmts_to_whyml`) plus F-mapbuild/F-set/F-irrec modeling gaps — genuine focused-feature work
   (spike→implement→gate), not loop grinding. `_symtype_to_whyml` and the map builders that call it are a
   natural ordering: convert the str-mapping leaves first, then the F-mapbuild family that consumes them.

Report path: `/tmp/claude-1346829620/-home-fabrice-derepas-canonical-com-git-pycsl/9dd932d0-43ec-4eaf-b2b4-3686bbb5f588/scratchpad/triage-A5.md`
