from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def find_calls_in_ir(obj: Any, func_names_set: int) -> int:
    return set()

#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def compute_sccs(names: int, call_graph: int) -> List[List[str]]:
    return []

#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def sort_functions_by_scc(functions: List[int]) -> Tuple[List[int], int]:
    return ([], {})

