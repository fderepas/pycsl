from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple
from module6_whyml.identifiers import whyml_ident, safe_exc_name
from module6_whyml.ir_scanner import IRScanner
from module6_whyml.scc import emits_as_logic_symbol
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
    def _callable_whyml_arrow(self, symtype: str) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _callable_tag_to_whyml(self, tag: str) -> str:
        """Map a single Callable arg/return PyCSL tag to its WhyML type."""
        if tag in ("int", "bool"):
            return "int"
        if tag == "str":
            return "string"
        if tag == "float":
            return "real"
        record_types = getattr(self, "_record_types", {})
        if tag in record_types:
            return record_types[tag]["whyml_name"]
        variant_types = getattr(self, "_variant_types", {})
        if tag in variant_types:
            return variant_types[tag]["whyml_name"]
        # Unknown bare name — sound fallback to `int`; Why3 rejects a mismatched
        # application rather than admitting an unsound type.
        return "int"

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
    def _has_dynamic_exec(self, func: int) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _compute_scope_sets(self, func: int):
        pass

    #@ requires True
    #@ ensures True
    #@ assigns acc
    def _collect_assign_targets(self, node: Any, acc: Set[str]) -> None:
        """Recursively gather Assign/AugAssign simple-name targets anywhere in a stmt subtree."""
        if isinstance(node, dict):
            if node.get("stmt") in ("Assign", "AugAssign") and isinstance(node.get("target"), str):
                acc.add(node["target"])
            for v in node.values():
                self._collect_assign_targets(v, acc)
        elif isinstance(node, list):
            for v in node:
                self._collect_assign_targets(v, acc)

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
    def _emit_contracts(self, contracts: int, spec_refs: int, func_variants: List[Any], func_diverges: bool, func_exceptions: int, func_is_noreturn: bool=False) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_narrowing_vc(self, name: str, args_str: str, return_type: str, defc: int, iface: int, spec_refs: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_union_arm_vc(self, name: str, symbol_table: int) -> List[str]:
        return []
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _union_arm_whyml_type(self, tag: str) -> str:
        """Map a Union arm IR type tag to its WhyML type string."""
        m = {"int": "int", "bool": "int", "str": "string", "float": "real",
             "list": "array int", "bytes": "array int", "bytearray": "array int",
             "dict": "map int (option int)", "set": "map int (option int)",
             "frozenset": "map int (option int)", "tuple": "array int"}
        return m.get(tag, "int")

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _returns_string_seq(self, body_stmts: List[int]) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _first_tuple_return_elts(self, stmts: List[int]) -> Optional[List[int]]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _infer_tuple_slot_type(self, elt: int, array_vars: int, dict_vars: int, symtab: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _refine_tuple_return_type(self, func: int, body_stmts: List[int], return_type: str) -> str:
        return ""

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
    def _emit_subtyping_goals(self, functions: List[int]) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _render_refinement_goal(self, ov: int, sub_fn: int, base_fn: int) -> List[str]:
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
    def _build_method_result_ensures_map(self, functions: List[int]) -> Dict[str, List[int]]:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_method_param_result_ensures_map(self, functions: List[int]) -> Dict[str, List[int]]:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_method_field_result_ensures_map(self, functions: List[int]) -> Dict[str, List[int]]:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_method_field_param_result_ensures_map(self, functions: List[int]) -> Dict[str, List[int]]:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_method_writes_map(self, functions: List[int]) -> Dict[str, List[str]]:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_method_field_old_ensures_map(self, functions: List[int]) -> Dict[str, List[int]]:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_method_field_param_post_ensures_map(self, functions: List[int]) -> Dict[str, List[int]]:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_method_field_param_frame_ensures_map(self, functions: List[int]) -> Dict[str, List[int]]:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_method_result_frame_ensures_map(self, functions: List[int]) -> Dict[str, List[int]]:
        return {}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _symtype_to_whyml(symtype: Optional[str]) -> str:
        """Convert a Module5 symbol-table type tag to the WhyML type used
        in abstract val parameter declarations. Defaults to `int`."""
        if symtype in ("set", "dict", "frozenset"):
            return "map int (option int)"
        if symtype in ("list", "tuple", "bytes", "bytearray"):
            # 0442.md B2 (no-more-int): bytes/bytearray are the byte-buffer array class.
            return "array int"
        if symtype == "str":
            return "string"
        if symtype == "float":
            return "real"  # no-more-int Stage D
        # typed-ir-for-b-ceiling.md B-C2: an `ExprIR`/`StmtIR`/`IRNode`-annotated
        # param or field is the typed IR-node sum `exprir` (§2.1), so an inline
        # `{"type": K}` construction and a real IR field unify at a sibling that takes
        # both. Only present in a @mutable_state mirror → byte-identical for the corpus.
        if symtype in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR", "exprir"):
            return "emit_ir"
        return "int"

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _parse_mixin_sig(sig: str):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _mixin_dep_pseudo_functions(self, functions: List[int]) -> List[int]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_method_param_types_map(self, functions: List[int]) -> Dict[str, List[str]]:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_method_param_whyml_types_by_name(self, functions: List[int]) -> int:
        return {}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_method_return_annotation_map(
            self, functions: List[Dict[str, Any]]) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for func in functions:
            ann = func.get("return_annotation")
            if ann:
                result[func["name"]] = ann
        return result


