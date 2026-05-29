from __future__ import annotations
#@ proof rocq Phase5b_Soundness.pycsl_soundness
#@ proof lean PyCSL.Soundness.pycsl_soundness
import json
from typing import Any, Dict, List, Optional, Set
from module6_whyml.identifiers import whyml_ident
from module6_whyml.scc import sort_functions_by_scc
from module6_whyml.auto_trust import AutoTrustMixin
from module6_whyml.abstract_ops import AbstractOpsMixin
from module6_whyml.types import TypeInferenceMixin
from module6_whyml.expressions import ExpressionEmissionMixin
from module6_whyml.statements import StatementEmissionMixin
from module6_whyml.preamble import PreambleEmissionMixin
from module6_whyml.functions import FunctionEmissionMixin
""  # pycsl
class Module6_WhyMLTranspiler(ExpressionEmissionMixin, StatementEmissionMixin, PreambleEmissionMixin, FunctionEmissionMixin, TypeInferenceMixin, AutoTrustMixin, AbstractOpsMixin):
    'Reads the JSON IR and transpiles it into valid WhyML (.mlw) syntax.'
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self, json_ir: str, memory_model: str='hoare', strict_no_exception_propagation: bool=False, strict_hash_eq_consistency: bool=False) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @property
    def _heap_var(self) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_callee_no_exception_summary(self, functions: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _callee_implicit_exceptions(self, callee_name: str) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _wrap_unannotated_call_with_strict_assert(self, inner: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _wrap_call_with_callee_raises_assert(self, callee_name: str, inner: str, args: List[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _render_callee_condition(self, cond_ir: Any, param_names: List[str], args: List[str]) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _wrap_with_no_exception_assert(self, op_key, operands, inner_expr: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _maybe_emit_no_exception_assert(self, op_key, operands) -> str:
        return ""

    _EXPR_DISPATCH: int = {'BinOp': '_handle_binop', 'Call': '_handle_call_expr', 'Subscript': '_handle_subscript', 'Attribute': '_handle_attribute_expr', 'FString': '_handle_fstring_expr', 'UnaryOp': '_handle_unaryop_expr', 'Old': '_handle_old_expr', 'At': '_handle_at_expr', 'IfExpr': '_handle_ifexpr_expr', 'NamedExpr': '_handle_named_expr_expr', 'SliceAccess': '_handle_slice_access_expr', 'ArrayLen': '_handle_arraylen_expr', 'Valid': '_handle_valid_expr', 'Separated': '_handle_separated_expr', 'Length2D': '_handle_length2d_expr', 'Valid2D': '_handle_valid2d_expr', 'IsSorted': '_handle_issorted_expr', 'Sum': '_handle_sum_node_expr', 'Lambda': '_handle_lambda_expr', 'SetLit': '_handle_setlit_expr', 'MkTuple': '_handle_mktuple_expr', 'FstExpr': '_handle_fst_expr', 'SndExpr': '_handle_snd_expr', 'ProjExpr': '_handle_proj_expr', 'StrConcat': '_handle_strconcat_expr', 'StrLength': '_handle_str_length_expr', 'StrSub': '_handle_str_sub_expr', 'GhostCopy': '_handle_ghost_copy_expr', 'GhostCopyRange': '_handle_ghost_copy_range_expr', 'GhostMake': '_handle_ghost_make_expr', 'MapEmpty': '_handle_map_empty_expr', 'MapGet': '_handle_map_get_expr', 'MapSet': '_handle_map_set_expr', 'MapEq': '_handle_map_eq_expr', 'HasKey': '_handle_has_key_expr', 'MapRemove': '_handle_map_remove_expr', 'SetEmpty': '_handle_set_empty_expr', 'SetAdd': '_handle_set_add_expr', 'SetRemove': '_handle_set_remove_expr', 'SetMem': '_handle_set_mem_expr', 'SetUnion': '_handle_set_union_expr', 'SetInter': '_handle_set_inter_expr', 'SetDiff': '_handle_set_diff_expr', 'SetCard': '_handle_set_card_expr', 'SetSubset': '_handle_set_subset_expr', 'SetEq': '_handle_set_eq_expr', 'Nil': '_handle_nil_expr', 'Cons': '_handle_cons_expr', 'Hd': '_handle_hd_expr', 'Tl': '_handle_tl_expr', 'ListLength': '_handle_list_length_expr', 'Nth': '_handle_nth_expr', 'Mem': '_handle_mem_expr', 'Append': '_handle_append_expr'}
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def transpile(self) -> str:
        return ""


