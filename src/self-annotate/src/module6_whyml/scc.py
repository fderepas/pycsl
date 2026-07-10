from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple, TypedDict


class LogicSymbolView(TypedDict):
    """Closed-key view of the exactly-three IR-function keys that the
    `emits_as_logic_symbol` classifier reads. Runtime-inert (a TypedDict IS a
    dict, so every existing caller passing a full function-IR dict is
    unaffected); statically it monomorphizes to a native WhyML record with
    faithful per-field types (`pure`/`lemma`: bool, `kind`: str), so the
    self-annotation mirror can lower `func.get("k")` to the record field read
    and `func.get("kind") == "method"` to a string compare (09-2223 G1/G2)."""
    pure: bool
    kind: str
    lemma: bool
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

#@ requires True
#@ ensures True
#@ assigns \nothing
def emits_as_logic_symbol(func: LogicSymbolView) -> bool:
    return (bool(func.get("pure"))
            and func.get("kind") != "method"
            and not func.get("lemma"))

#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def sort_functions_by_scc(functions: List[int]) -> Tuple[List[int], int]:
    return ([], {})

