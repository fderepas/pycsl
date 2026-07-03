from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from module6_whyml.identifiers import op_translate, whyml_ident, stable_hash
from module6_whyml.struct_format import parse_format
from module6_whyml.expr_ghost_collections import GhostCollectionOpsMixin
from module6_whyml.expr_ghost_spec_ops import GhostSpecOpsMixin
# self-tcb-reduction T1.a (E-2): import the concrete ExprIR subclasses the handlers annotate, so
# `node: "UnaryOpExpr"` resolves to a record (fields `op`/`expr`), like the statement mirror's
# `stmt: AssignStmt`. The base `node: "ExprIR"` handlers use the emit_ir keystone instead.
from ir_schema import AtExpr, IfExprExpr, NamedExprExpr, OldExpr, UnaryOpExpr
def mutable_state(cls): return cls
""  # pycsl
# self-tcb-reduction T1.a: mark the expression mixin @mutable_state so the emit_ir ADT + the
# string/reflection recognizers fire for the un-`\trusted` `_handle_*_expr` bodies (the CF0 analog).
@mutable_state
@dataclass
class ExpressionEmissionMixin(GhostCollectionOpsMixin, GhostSpecOpsMixin):
    # State fields the ported expression handlers read (declared for @dataclass / @mutable_state).
    _all_record_fields: Set[str] = None
    _array_locals: Set[str] = None
    _class_constants: Dict[str, Any] = None
    _constructors: Dict[str, Any] = None
    _current_params: Set[str] = None
    _current_self_type: str = ""
    _emit_record_ctx: str = ""
    _lambda_locals: Set[str] = None
    _module_constants: Dict[str, Any] = None
    _module_global_classes: Dict[str, str] = None
    _quant_record_binders: Dict[str, str] = None
    _quant_scalar_binders: Set[str] = None
    _record_locals: Set[str] = None
    _record_types: Dict[str, Any] = None
    _shared_var_names: Set[str] = None
    _todict_aliases: Dict[str, str] = None
    _current_symbol_table: Dict[str, str] = None
    _mutable_state_classes: Set[str] = None
    'Expression-emission dispatch: every IR expression-shape `_handle_*_expr`\n    handler routed via `_EXPR_DISPATCH` on the facade, plus the orchestration\n    entrypoints (`_expr_to_whyml`, `_expr_to_whyml_string_ctx`) and the shared\n    helpers (`_to_bool`, `_coerce_*`, `_match_pattern_cond`, ...). Mixed into\n    Module6_WhyMLTranspiler. `_EXPR_DISPATCH` stays on the facade as a class\n    attribute — moving it would force a circular import.\n    '
    _BITWISE_FOLD_OPS = {'&': lambda a, b: a & b, '|': lambda a, b: a | b, '^': lambda a, b: a ^ b, '<<': lambda a, b: a << b, '>>': lambda a, b: a >> b, '**': lambda a, b: a ** b}
    _BITWISE_FN_NAMES = {'&': 'bit_and', '|': 'bit_or', '^': 'bit_xor', '<<': 'bit_lshift', '>>': 'bit_rshift', '**': 'py_pow'}

    # self-tcb-reduction T1.a: sibling stubs the ported expression handlers call cross-mixin.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _add_abstract_op(self, decl: str) -> None:
        return

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _is_emit_ir_expr(self, ir: "ExprIR") -> bool:
        return False
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _e(self, ir: Dict, lr: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _to_bool(self, whyml_str: str, ir_expr: "ExprIR") -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _coerce_str_arg(whyml_str: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _materialize_if_seq(self, whyml_str: str, arg_ir: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _array_coerce_arg(whyml_str: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _deref(self, expr: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _coerce_to_int(self, whyml_str: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _dv_empty_default(self, nu: Optional[str]) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _dv_missing_default(self, nu: Optional[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _dv_store_value(self, nu: Optional[str], val_expr: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _match_pattern_cond(self, pat: int, subject: str, local_refs: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_membership(self, op: str, expr: int, left: str, right: str, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_bitwise_or_power(self, op_char: str, expr: int, left: str, right: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _is_string_expr(self, ir: "ExprIR") -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _is_float_expr(self, ir: int) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _str_operand_to_int(self, whyml_str: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_binop(self, expr: int, local_refs: int, invariant_ctx: bool=False, subst: int=None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _iter_len_expr(self, ir: int, local_refs: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_len_call(self, expr: int, args: List[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_join_call(self, expr: int, args: List[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_sum_call(self, expr: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _resolve_dotted_signature(self, func_name: str):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_dotted_call(self, func_name: str, args: List[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _coerce_dotted_args(self, args: List[str], param_types: List[str]) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _strip_outer_parens(s: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _frame_trigger_term(self, node: Any) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _dotted_ensures_suffix(self, result_ensures: List[int], n: int, param_types: List[str], field_spec: Optional[Any]=None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_struct_call(self, expr: int, args: List[str], func_name: str) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_contract_logic_symbol(self, func_name: str, expr: int, args: List[str]) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _is_null_byte_lit(ir: int) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _linear_form(self, ir: int) -> int:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _static_width(self, lower_ir: int, upper_ir: int) -> int:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _match_field_decode_idiom(self, expr: int) -> Optional[tuple]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _recognize_field_decode_idiom(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_call_expr(self, expr: int, local_refs: int, invariant_ctx: bool=False, subst: int=None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _content_string_method(self, expr: int, args: List[str], func_name: str, local_refs: int, invariant_ctx: bool, subst: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _call_named_builtins(self, expr: int, args: List[str], func_name: str, local_refs: int=None, invariant_ctx: bool=False, subst: int=None) -> Optional[str]:
        return None

    _METATYPE_TAGS = {'int': 'tag_int', 'bool': 'tag_int', 'str': 'tag_str', 'float': 'tag_float', 'list': 'tag_list', 'List': 'tag_list', 'dict': 'tag_dict', 'Dict': 'tag_dict', 'set': 'tag_dict', 'frozenset': 'tag_dict', 'object': 'tag_object'}
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_metatype_tags(self) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _tag_of_type(self, t_name: Optional[str]) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _tag_of_value(self, x_ir: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _union_none_ctor_for(self, x_ir: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_isinstance(self, expr: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _subst_params(self, ir: Any, arg_nodes: int) -> Any:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _call_record_constructor(self, args: List[str], func_name: str) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _call_bytes_methods(self, args: List[str], func_name: str) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _typeddict_field_access(self, value: int, index_ir: int, local_refs: int, invariant_ctx: bool, subst: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _typeddict_record_literal(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _namedtuple_positional_access(self, value: int, index_ir: int, local_refs: int, invariant_ctx: bool, subst: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_subscript(self, expr: int, local_refs: int, invariant_ctx: bool=False, subst: int=None) -> str:
        return ""
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_attribute_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_var_expr(self, expr: int, local_refs: int, subst: int=None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _quant_binder_whyml(self, binder_type: Optional[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _push_quant_binder(self, var: Optional[str], binder_type: Optional[str]):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _pop_quant_binder(self, var: Optional[str], token) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _field_label(self, record_lower: Optional[str], field: str) -> str:
        return ""
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_field_get_expr(self, expr: int, invariant_ctx: bool) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_fstring_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_unaryop_expr(
        self,
        node: "UnaryOpExpr",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        # Phase-B-expr: typed. `node` is a UnaryOpExpr (op: str, expr: ExprIR).
        e = self._expr_to_whyml(node.expr, local_refs, invariant_ctx, subst)
        op = op_translate(node.op)
        if op == "+":
            return e
        if op == "~":
            # 0442.md C4: Python bitwise NOT on the int model is the two's-complement
            # identity `~x == -x - 1` (genuine int op, not a type-class leak).
            return f"((- {e}) - 1)"
        if op == "not":
            e = self._to_bool(e, node.expr.to_dict())
        return f"({op} {e})"

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_old_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_at_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_ifexpr_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_named_expr_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_slice_access_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_arraylen_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _module_binding_names(self) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_in_globals_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_in_scope_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_valid_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_separated_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_length2d_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_valid2d_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_issorted_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_arrayeq_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_permutation_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_sum_node_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_lambda_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_setlit_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _expr_to_whyml(self, expr: "ExprIR", local_refs: Set[str], invariant_ctx: bool=False, subst: Optional[Dict[str, str]]=None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _expr_to_whyml_string_ctx(self, ir: "ExprIR", local_refs: int) -> str:
        return ""


