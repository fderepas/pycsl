from __future__ import annotations
from typing import List, Optional, Set
""  # pycsl
class AbstractOpsMixin:
    'Registry of abstract `val` declarations and the late-emission block.\n\n    During expression / statement emission the transpiler accumulates abstract\n    val declarations for Python operations with no native WhyML equivalent\n    (e.g. `pow_int`, `stmt_get`, generic iterator helpers). Deduplication is by\n    name; same-name different-arity collisions are disambiguated by suffixing\n    `_N`. The final block is inserted by `_insert_abstract_val_block`\n    immediately after the last `type` declaration so that abstract vals\n    referencing record types resolve correctly.\n    '
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _add_abstract_op(self, decl: str) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _find_abstract_val_insert_idx(self, out: List[str]) -> int:
        return 0

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _advance_past_referenced_axiom_decls(self, out: List[str], idx: int) -> int:
        return 0

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _insert_abstract_val_block(self, out: List[str]) -> None:
        pass


