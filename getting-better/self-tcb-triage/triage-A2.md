# Triage A2 — src/self-annotate/src/frontend/Module5_IREmitter.py (180 \trusted stubs)

Transcription source: `src/pycsl/frontend/Module5_IREmitter.py` (4614 lines live).
Method: static classification against the recognizer stack + known-gaps; ONE spot-check
(`_mixin_field_type`, reverted). This is the **AST -> IR emitter**: almost every method either
consumes a typed AST node (Python `ast.*` or a `CSLNode` variant from Module2_Parser) via
`isinstance`/`type()` dispatch, and/or constructs a heterogeneous IR node **dict**
(`{"type": K, ...}`). Both are the canonical *hard-architectural* blockers.

## Per-bucket counts
| bucket | count |
|---|---|
| trivial-leaf | 0 |
| needs-recognizer | 2 |
| hard-architectural | 178 |
| floor | 0 |

There are **no batch-convertible cheap wins** in this file. Even the single pure-scalar helper
that looked trivial leaks (see spot-check).

## Classification by family

| stub family | #stubs | bucket | reason |
|---|---|---|---|
| `_csl_*` (`_csl_to_ir`, `_csl_binop`, `_csl_var`, `_csl_number`, `_csl_string`, `_csl_forall`, `_csl_set_*`, `_csl_map_*`, `_csl_list_*`, ... ) | 75 | hard-architectural | consume a typed `CSLNode` variant (reads `.value`/`.name`/`.left`/`.op`) and RETURN an `emit_ir` dict `{"type": K, ...}`. Needs (a) every CSL* dataclass modeled as a record/variant AND (b) the emit_ir ADT to carry an arm for each of ~70 distinct `{"type":K}` shapes. Not one recognizer. |
| `_py_expr_*` (`_py_expr_name`, `_binop`, `_call`, `_subscript`, `_listcomp`, `_fstring`, ...) + `_py_expr_to_ir` | 23 | hard-architectural | dispatch on Python `ast.*` node type (`_PY_EXPR_HANDLERS` keyed by `type(expr)`), read AST fields, build IR dicts. Needs Python-AST-node value model + `type()`-keyed variant dispatch + emit_ir construction. |
| `_py_stmt_*` (`_assign`, `_for`, `_if`, `_while`, `_try`, `_match`, ...) + `_py_stmts_to_ir` | 17 | hard-architectural | consume `ast.stmt`, mutate an `ir_stmts: List[int]` accumulator with constructed IR nodes. AST-node model + IR-node list append. |
| `_process_while/_process_for/_process_if` | 3 | hard-architectural | build loop/if IR nodes from ast. Same blocker. |
| `visit_Module`, `visit_ClassDef`, `visit_FunctionDef` | 3 | hard-architectural | top-level NodeVisitor walkers; large stateful AST traversal driving the whole emit. |
| `_is_*` (`_is_typeddict_class`, `_is_namedtuple_class`, `_is_protocol_class`, `_is_overload_stub`, `_is_final_annotation`, `_is_decode_call`) | 6 | hard-architectural | bool predicates via `isinstance` chains over `ast.ClassDef`/`FunctionDef`/`Constant`/decorators. AST-node model + isinstance dispatch. |
| annotation->str helpers (`_field_type_from_annotation(_inst)`, `_m5_get_type_name(_legacy)`, `_m5_get_dict_value/key_type`, `_callable_type_tag`, `_encode_callable_annotation`, `_wrap_optional`, `_typeddict_field_type`, `_union_arm_tag`, `_collect_union_arms`, `_normalize_union/final/literal_annotation`, `_overload_type_name`) | ~18 | hard-architectural | take `annotation: ast.expr`, `isinstance`-walk it, sometimes SYNTHESIZE new ast nodes (`_wrap_optional` builds `ast.Subscript`) or raise. Pure AST consumers. |
| int/tuple-from-ast (`_const_int_value`, `_array_init_size`, `_classify_literal_value`) | 3 | hard-architectural | `isinstance(x, ast.Constant/UnaryOp)` scalar extraction; `_classify_literal_value` returns a `(str, Any, dict)` tuple with an emit_ir node. |
| IR-reflection walkers (`_scan_2d_in_expr/_stmt`, `_collect_2d_params`, `_detect_array_dimensions`, `_detect_seq_promotion`, `_collect_str_decode_locals`, `_is_decode_call`) | ~6 | hard-architectural | take `int` IR-node ids and reflect on IR structure recursively; IR-node value model over recursion. |
| record/synthesis emitters (`_emit_typeddict_record`, `_emit_namedtuple_record`, `_emit_protocol_interface`, `_populate_protocol_conformance`, `_synthesize_typeddict/namedtuple_functional`, `_synthesize_overload_guard`, `_build_overload_param_guard`, `_collect_class_fields/constants`, `_collect_type_params`, `_extract_generic_arg_names`, `_collect_typevar_registry`, `_collect_final_registry`) | ~15 | hard-architectural | walk `ast.ClassDef`/`Module`, build records + emit_ir. AST-node model + IR construction. |
| build/dispatch glue (`_build_function_symbol_table`, `_build_function_ir`, `_py_op_to_str`, `_comprehension_generators_to_ir`, `_emit_ghost_assign`, `_match_pattern_to_ir`, `_get_mutex_invariant_ir`, `_should_skip_method`, `__init__`) | ~9 | hard-architectural | `_py_op_to_str` = dict keyed by `type(op)` (type-object keys); `_get_mutex_invariant_ir` calls the still-trusted `_csl_to_ir` stub + returns emit_ir/None union; `__init__` = large stateful field init; rest AST/IR. |
| **`_mixin_field_type`** (`type_str: str -> str`) | 1 | **needs-recognizer: string-literal-in-if-expr-return not typed as string (coerced to int-hash)** | SPOT-CHECKED. Pure string: `.strip()`, `or "int"` (both-string, supported), `in (tuple of str literals)` (works -> `str_eq_op`). LEAK: `return "list" if t=="array" else t` lowered `"list"` to int hash `1555321514` (then-branch string literal mistyped int because the if-expr result type resolved to int from the `else` string-local). One bounded fix. |
| **`_fresh_var`** (`-> str`) | 1 | **needs-recognizer: mixed str/int f-string interpolation (int field -> string)** | `f"{prefix}_{self._fresh_var_counter}"` interpolates an `int` counter into a string (all-string f-string is supported per B2; the int component is not) + mutates `self._fresh_var_counter` (needs the field declared `@mutable_state int` and in the frame). |

## Feature fan-out (this group)
| feature / architectural blocker | #stubs | example stubs |
|---|---|---|
| AST/variant-node value model + emit_ir IR-node (dict) construction + type/isinstance variant dispatch (the whole emitter's core) | 178 | `_csl_*` (75), `_py_expr_*` (23), `_py_stmt_*` (17), `visit_*`, `_is_*`, annotation->str helpers |
| — sub-blocker: `CSLNode` variant records + emit_ir arm per `{"type":K}` shape | 75 | `_csl_number`, `_csl_var`, `_csl_string`, `_csl_bool`, `_csl_none`, ... |
| — sub-blocker: Python `ast.*` node model + `type()`-keyed dispatch table | ~46 | `_py_expr_to_ir`, `_py_op_to_str`, `_py_stmt_*`, `_process_*` |
| string-literal-in-if-expr-return typed as string (not int-hash) | 1 | `_mixin_field_type` |
| mixed str/int f-string interpolation | 1 | `_fresh_var` |

## Notes / honesty
- **Least-hard within hard-architectural** (candidate first targets IF a CSL-node-record +
  emit_ir-arm model ever lands): `_csl_number`, `_csl_var`, `_csl_string`, `_csl_bool`, `_csl_none`
  — each is a single-field emit_ir dict from one CSL-node field. Still gated behind the same
  two deep modeling features, so per the "≥2 deep features -> defer" rule they are NOT
  pickups now; flagged only so the orchestrator knows where the cheapest hard-family entry is.
- The two `needs-recognizer` stubs are the only near-term-plausible conversions here, and each
  needs a distinct small emitter feature (fan-out 1 each) — low leverage; likely better picked up
  opportunistically if those recognizers land for other files.
- No `floor` stubs (no recursion-leaf/D2-axiom boundary in this file; the recursion is over
  AST/IR, which is the hard-architectural model, not an irreducible floor).
- Spot-check was reverted; `git status` clean on the mirror file.
