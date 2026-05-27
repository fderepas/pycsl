from __future__ import annotations

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


class Module6_WhyMLTranspiler(
    ExpressionEmissionMixin,
    StatementEmissionMixin,
    PreambleEmissionMixin,
    FunctionEmissionMixin,
    TypeInferenceMixin,
    AutoTrustMixin,
    AbstractOpsMixin,
):
    """Reads the JSON IR and transpiles it into valid WhyML (.mlw) syntax."""

    def __init__(self, json_ir: str, memory_model: str = "hoare") -> None:
        self.ir = json.loads(json_ir)
        self.memory_model = memory_model   # "hoare" | "typed" | "store"
        self._abstract_ops: Dict[str, str] = {}  # Abstract val declarations: name → full decl string
        self._record_types: Dict[str, Any] = {}  # class_name_lower → {fields: [...], defaults: {...}}
        self._shared_var_names: Set[str] = set()  # Module-level shared variable names (concurrent model)
        self._havoc_counter: int = 0             # Counter for unique havoc variable names
        self._in_spec: bool = False              # True when emitting contracts (no div-by-zero VCs)
        # Per-function state — reset per function via `_reset_function_state`;
        # initialised here so they're always defined and accessing them
        # before the first reset is safe.
        self._bounded_int: Optional[int] = None
        self._array2d_params: Set[str] = set()
        self._current_array1d_params: Set[str] = set()
        self._current_params: Set[str] = set()
        self._current_symbol_table: Dict[str, Any] = {}
        self._array_locals: Set[str] = set()
        self._dict_locals: Set[str] = set()
        self._record_locals: Set[str] = set()
        self._lambda_locals: Set[str] = set()
        self._current_self_type: Optional[str] = None
        self._func_return_type: str = "int"
        self._current_tuple_arity: int = 0
        self._has_early_ret: bool = False
        self._for_idx_init: str = "0"
        # Whole-module state — populated by `transpile()` before any
        # function emission; initialised empty so type-check passes and
        # accidental early access yields a clean empty default.
        self._all_record_fields: Set[str] = set()
        self._module_func_names: Set[str] = set()
        self._module_method_return_types: Dict[str, str] = {}
        self._module_method_param_types: Dict[str, List[str]] = {}
        self._auto_trusted_array_returns: List[str] = []
        self._auto_trusted_tuple_returns: List[str] = []
        self._auto_trusted_map_returns: List[str] = []
        self._auto_trusted_set_op: List[str] = []

    @property
    def _heap_var(self) -> str:
        """Returns the name of the mutable heap variable for the current model."""
        if self.memory_model == "typed":
            return "int_mem"
        elif self.memory_model == "store":
            return "store"
        raise ValueError(f"No heap variable in Hoare model")

    _EXPR_DISPATCH: Dict[str, str] = {
        "BinOp":        "_handle_binop",
        "Call":         "_handle_call_expr",
        "Subscript":    "_handle_subscript",
        "Attribute":    "_handle_attribute_expr",
        "FString":      "_handle_fstring_expr",
        "UnaryOp":      "_handle_unaryop_expr",
        "Old":          "_handle_old_expr",
        "At":           "_handle_at_expr",
        "IfExpr":       "_handle_ifexpr_expr",
        "NamedExpr":    "_handle_named_expr_expr",
        "SliceAccess":  "_handle_slice_access_expr",
        "ArrayLen":     "_handle_arraylen_expr",
        "Valid":        "_handle_valid_expr",
        "Separated":    "_handle_separated_expr",
        "Length2D":     "_handle_length2d_expr",
        "Valid2D":      "_handle_valid2d_expr",
        "IsSorted":     "_handle_issorted_expr",
        "Sum":          "_handle_sum_node_expr",
        "Lambda":       "_handle_lambda_expr",
        "SetLit":       "_handle_setlit_expr",
        # Ghost expression types
        "MkTuple":      "_handle_mktuple_expr",
        "FstExpr":      "_handle_fst_expr",
        "SndExpr":      "_handle_snd_expr",
        "ProjExpr":     "_handle_proj_expr",
        "StrConcat":    "_handle_strconcat_expr",
        "StrLength":    "_handle_str_length_expr",
        "StrSub":       "_handle_str_sub_expr",
        "GhostCopy":      "_handle_ghost_copy_expr",
        "GhostCopyRange": "_handle_ghost_copy_range_expr",
        "GhostMake":      "_handle_ghost_make_expr",
        "MapEmpty":     "_handle_map_empty_expr",
        "MapGet":       "_handle_map_get_expr",
        "MapSet":       "_handle_map_set_expr",
        "MapEq":        "_handle_map_eq_expr",
        "HasKey":       "_handle_has_key_expr",
        "MapRemove":    "_handle_map_remove_expr",
        "SetEmpty":     "_handle_set_empty_expr",
        "SetAdd":       "_handle_set_add_expr",
        "SetRemove":    "_handle_set_remove_expr",
        "SetMem":       "_handle_set_mem_expr",
        "SetUnion":     "_handle_set_union_expr",
        "SetInter":     "_handle_set_inter_expr",
        "SetDiff":      "_handle_set_diff_expr",
        "SetCard":      "_handle_set_card_expr",
        "SetSubset":    "_handle_set_subset_expr",
        "SetEq":        "_handle_set_eq_expr",
        "Nil":          "_handle_nil_expr",
        "Cons":         "_handle_cons_expr",
        "Hd":           "_handle_hd_expr",
        "Tl":           "_handle_tl_expr",
        "ListLength":   "_handle_list_length_expr",
        "Nth":          "_handle_nth_expr",
        "Mem":          "_handle_mem_expr",
        "Append":       "_handle_append_expr",
    }

    def transpile(self) -> str:
        """Entry point: converts the entire program to a .mlw string."""
        functions = self.ir.get("functions", [])
        type_decls = self.ir.get("type_decls", [])
        all_bodies = [func["body"] for func in functions]

        self._all_record_fields = self._collect_record_fields(type_decls)

        needs = self._scan_preamble_needs(functions, all_bodies)
        out = self._emit_preamble(needs)
        out += self._emit_shared_state()

        type_lines, declared_types = self._emit_type_decls(type_decls)
        out += type_lines

        self._emit_opaque_class_aliases(functions, out, declared_types)

        self._module_func_names = {whyml_ident(func["name"]) for func in functions}
        self._module_method_return_types = self._build_method_return_type_map(functions)
        self._module_method_param_types = self._build_method_param_types_map(functions)

        sorted_functions, scc_info = sort_functions_by_scc(functions)
        for func in sorted_functions:
            out += self._emit_function(func, scc_info)

        out.append("end")
        self._insert_abstract_val_block(out)
        return "\n".join(out)
