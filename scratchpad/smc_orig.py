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

#@ requires True
#@ ensures True
#@ assigns \nothing
def find_self_method_calls(obj: Any, self_type: str,
                           func_names_set: Set[str],
                           concrete_set: Set[str]) -> Set[str]:
    """allocator-frame plan §2.7: a `self.<m>(...)` call to a `#@ sibling_concrete` callee
    lowers (see expressions._handle_dotted_call) to a CONCRETE `(<class>__<m> self args)`
    call, so the callee must be emitted BEFORE this caller. Its `Call` node's `func` is the
    dotted `"self.<m>"`, not the method's IR name `"<class_lower>__<m>"`, so `find_calls_in_ir`
    misses it. Resolve those here, given the enclosing method's `self_type`, and return the
    resolved names that ARE real functions AND opted in (`concrete_set`) — i.e. the ordering
    edges the concrete calls actually need. Restricting to `concrete_set` avoids spurious
    edges (potential cycles) for the abstract-stub self-calls. No-op when self_type falsy."""
    if not self_type or not concrete_set:
        return set()
    prefix = self_type.lower() + "__"
    out: Set[str] = set()
    if isinstance(obj, dict):
        f = obj.get("func")
        if obj.get("type") == "Call" and isinstance(f, str) and f.startswith("self."):
            resolved = prefix + f[len("self."):]
            if resolved in func_names_set and resolved in concrete_set:
                out.add(resolved)
        for v in obj.values():
            out |= find_self_method_calls(v, self_type, func_names_set, concrete_set)
    elif isinstance(obj, list):
        for item in obj:
            out |= find_self_method_calls(item, self_type, func_names_set, concrete_set)
    return out

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

