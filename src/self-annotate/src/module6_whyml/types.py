from __future__ import annotations
from typing import Any, Dict, List, Optional, Set
_BOOL_BINOPS = frozenset({'==', '!=', '<', '<=', '>', '>=', 'is', 'is not', 'in', 'not in'})
""  # pycsl
class TypeInferenceMixin:
    'Type inference and collection-metadata tracking for the transpiler.\n\n    Covers three concerns:\n\n    * **First-assignment classification** (`_first_assign_kind`,\n      `_emit_first_assign` callers): record vs lambda vs array vs dict vs\n      bounded-int vs default, used to pick the `let X = ...` shape.\n    * **RHS type queries** (`_rhs_yields_array`, `_rhs_yields_map`,\n      `_field_type_for`, `_field_type_of`): does this IR expression\n      produce an `array int` / `map int (option int)` / typed self-field?\n      Drives the dict-vs-array vs int slot choices throughout statement\n      emission.\n    * **Collection constant-folding metadata** (`_track_collection_metadata`):\n      records known sizes/elements of literal collections so `len(...)`\n      and `sum(...)` can fold to constants during expression emission.\n\n    Mixed into Module6_WhyMLTranspiler. State accessed via `self`:\n    `_record_types`, `_known_collection_sizes`, `_known_collection_elements`,\n    `_array_locals`, `_dict_locals`, `_current_symbol_table`,\n    `_current_array1d_params`, `_current_self_type`,\n    `_module_method_return_types`, `_bounded_int`, the various\n    `_ghost_*_vars` sets.\n    '
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _track_collection_metadata(self, target: str, val_ir: int) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _val_is_bool(val_ir: int) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _first_assign_kind(self, val: str, val_ir: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _rhs_yields_array(self, val_ir: int) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _rhs_yields_map(self, val_ir: int) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _resolve_effective_ghost_type(self, target: str, op: str, ghost_type: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _field_type_for(self, obj: str, field: str) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _field_type_of(self, attr_ir: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _bool_ir_to_int_wrap(self, val: str, val_ir: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_array_var_assigns(self, stmts: List[int]) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_dict_var_assigns(self, stmts: List[int]) -> int:
        return set()


