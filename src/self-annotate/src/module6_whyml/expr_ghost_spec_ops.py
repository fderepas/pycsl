from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
def mutable_state(cls): return cls
""  # pycsl
@mutable_state
@dataclass
class GhostSpecOpsMixin:
    "Ghost spec-operator leaf handlers for tuples, strings, and ghost arrays —\n    the non-collection counterpart of `GhostCollectionOpsMixin`:\n\n      * tuples:       `\\mktuple` / `\\fst` / `\\snd` / `\\proj`\n      * strings:      `\\strconcat` (`^`) / `\\str_length` / `\\str_sub`\n      * ghost arrays: `\\copy` / `\\copy_range` / `\\make`\n\n    Extracted verbatim from `ExpressionEmissionMixin` (Part B move 3d).\n    `ExpressionEmissionMixin` inherits this mixin, so the handlers resolve via\n    MRO through the facade's `_EXPR_DISPATCH` and call back into `self._e`,\n    `self._deref`, `self._expr_to_whyml_string_ctx`, and `self._ghost_tuple_vars`\n    (which stay in `ExpressionEmissionMixin`)."

    # Run #3 (z1), route #488 follow-up: the state fields named in this mixin's (now honest)
    # `#@ assigns` clauses, DECLARED so the emitted `writes` carries them instead of dropping them
    # (check-assigns-writes-survival TRAP). Annotations COPIED from ExpressionEmissionMixin's /
    # StatementEmissionMixin's declarations of the same live fields where one exists; the other
    # eight are typed from their LIVE initialisers/writes: `_late_content_ops: List[Any] = []`
    # appended `(op, decl, using)` with `using = getattr(self, "_current_emitting_func", None)`;
    # `_last_hval_get_raw/_str` assigned f-strings, read `getattr(self, ..., None)`;
    # `_uses_*_cache` assigned a bool `result`, read `getattr(self, ..., None)`.
    _abstract_ops: Dict[str, str] = None
    _comp_content_counter: int = 0
    _current_params: Set[str] = None
    _current_self_type: str = ""
    _dict_locals: Set[str] = None
    _frame_trigger_active: bool = False
    _func_return_type: str = ""
    _in_spec: int = 0
    _last_hval_get_raw: Optional[str] = None
    _last_hval_get_str: Optional[str] = None
    _late_content_ops: List[Tuple[str, str, Optional[str]]] = None
    _needs_array_init: bool = False
    _obj_state_written: bool = False
    _quant_record_binders: Dict[str, str] = None
    _quant_scalar_binders: Set[str] = None
    _string_local_vars: Set[str] = None
    _todict_arg_wants_pymap: bool = False
    _uses_build_param_list_cache: Optional[bool] = None
    _uses_compute_return_type_cache: Optional[bool] = None
    _uses_const_reflect_cache: Optional[bool] = None
    _uses_pyast_parser_cache: Optional[bool] = None
    _uses_refine_tuple_return_type_cache: Optional[bool] = None

    # item34.md CF0.3 pattern (mirrored from stmt_control_flow.py): cross-file
    # recursion-leaf / bridge sibling stubs for `_e`/`_expr_to_whyml_string_ctx`
    # (defined in `ExpressionEmissionMixin`, expressions.py, which this mixin
    # composes with at runtime). Standalone per-file verification of this mixin
    # cannot see that sibling class, so a same-named call would otherwise
    # auto-synthesize a generic int-typed stub; the local trusted redeclaration
    # types the param the way this file actually calls it (an ExprIR sub-node),
    # matching the already-tolerated mirror-only shim precedent.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache
    def _e(self, ir: "ExprIR", lr: Set[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache
    def _expr_to_whyml_string_ctx(self, ir: "ExprIR", lr: Set[str]) -> str:
        return ""

    # Route #488: RE-TRUSTED. The live body calls the writing `self._e` inside a list
    # comprehension, which PyCSL lowers opaquely and therefore REFUSES (ir-semantic: a writing
    # call inside an opaque comprehension). Its former `assigns \nothing` proof held only because
    # the local `_e` declaration understated `_e`'s definition frame. Honest contract: the
    # transitive frame of `_e` (the definition's 22 fields). See trusted-reasons.tsv.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache
    def _handle_mktuple_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache
    def _handle_fst_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        t = self._e(node.tuple, lr)
        safe_t = t.lstrip("!")
        return f"(let (x_, _) = !{safe_t} in x_)" if t.startswith("!") else f"(let (x_, _) = {t} in x_)"

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache
    def _handle_snd_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        t = self._e(node.tuple, lr)
        safe_t = t.lstrip("!")
        return f"(let (_, y_) = !{safe_t} in y_)" if t.startswith("!") else f"(let (_, y_) = {t} in y_)"

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache
    def _handle_proj_expr(self, node: int, lr: int, _ic: bool, _sub: int) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache
    def _handle_ctor_test_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        x = self._e({"type": "Var", "name": node.var}, lr)
        ctor = node.ctor
        arity = getattr(self, "_constructors", {}).get(ctor, {}).get("arity", 0)
        binders = (" " + " ".join(["_"] * arity)) if arity else ""
        return f"(match {x} with {ctor}{binders} -> true | _ -> false end)"

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache
    def _handle_ctor_payload_expr(self, node: int, lr: int, _ic: bool, _sub: int) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache
    def _handle_strconcat_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._expr_to_whyml_string_ctx(node.left.to_dict(), lr)
        r = self._expr_to_whyml_string_ctx(node.right.to_dict(), lr)
        # Why3 string.String exports 'concat' (not '^' or 'String.(^)')
        return f"(concat {l} {r})"

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache
    def _handle_str_length_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._expr_to_whyml_string_ctx(node.string.to_dict(), lr)
        return f"(String.length {s})"

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache
    def _handle_str_sub_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._expr_to_whyml_string_ctx(node.string.to_dict(), lr)
        lo = self._e(node.lo, lr)
        hi = self._e(node.hi, lr)
        return f"(String.substring {s} {lo} ({hi} - {lo}))"

    #@ requires True
    #@ ensures \result == "(Array.copy " + node.arr + ")"
    #@ assigns \nothing
    def _handle_ghost_copy_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        return f"(Array.copy {node.arr})"

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache
    def _handle_ghost_copy_range_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        lo = self._e(node.lo, lr)
        hi = self._e(node.hi, lr)
        return f"(Array.sub {node.arr} {lo} ({hi} - {lo}))"

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache
    def _handle_ghost_make_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        n = self._e(node.size, lr)
        v = self._e(node.default, lr)
        return f"(Array.make {n} {v})"


