from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple
from module6_whyml.identifiers import whyml_ident, safe_mutex_name
from module6_whyml.ir_scanner import IRScanner
""  # pycsl
class FunctionEmissionMixin:
    'Function-emission: signature assembly, parameter typing, contract emission, return-type computation, per-function state reset, and the cross-method type maps populated by `transpile()` before any function body is emitted. Mixed into Module6_WhyMLTranspiler.'
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _param_type_str(self, arg: str, ref_params: int, array2d_params: int, array1d_params: int, symbol_table: int, int_type: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_record_fields(self, type_decls: List[int]) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _reset_function_state(self, func: int, body_stmts: List[int]) -> int:
        return ([], {})

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_param_list(self, func: int, local_refs: int, ghost_vars: int) -> int:
        return ([], {})

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_contracts(self, contracts: int, spec_refs: int, func_variants: List[Any], func_diverges: bool, func_exceptions: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _compute_return_type(self, func: int, body_stmts: List[int]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_function(self, func: int, scc_info: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_method_return_type_map(self, functions: List[int]) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _symtype_to_whyml(symtype: Optional[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_method_param_types_map(self, functions: List[int]) -> Dict[str, List[str]]:
        return {}


