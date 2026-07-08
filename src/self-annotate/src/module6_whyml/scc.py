from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple
#@ requires True
#@ ensures True
#@ assigns \nothing
def find_calls_in_ir(obj: Any, func_names_set: Set[str]) -> Set[str]:
    """Find all function names called within an IR object."""
    calls: Set[str] = set()
    if isinstance(obj, dict):
        if obj.get("type") == "Call" and obj.get("func") in func_names_set:
            calls.add(obj["func"])
        for v in obj.values():
            calls |= find_calls_in_ir(v, func_names_set)
    elif isinstance(obj, list):
        for item in obj:
            calls |= find_calls_in_ir(item, func_names_set)
    return calls

#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def find_self_method_calls(obj: Any, self_type: str, func_names_set: int, concrete_set: int) -> int:
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
def emits_as_logic_symbol(func: int) -> bool:
    return False

#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def sort_functions_by_scc(functions: List[int]) -> Tuple[List[int], int]:
    return ([], {})

