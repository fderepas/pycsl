"""Test 0883 — bigger-build A-unit GenericFold NESTED-FIELD pre-action grammar (POSITIVE).

Exercises the generic `Dict[str, Any]` walk recognizer's NESTED-FIELD read pre-action
(the grammar delta landed with `_hp_collect_written`): a self-recursive walk that
projects a CHILD dict out of the node and gates a by-ref `Set[str]` add on a compound
guard over the child's literal keys (`arr.get("type") == "FieldGet"` and
`arr.get("object") == "self"`), then adds the child's `field`.

Lowers to the certified `pydict` catamorphism — the child projected as `Some (PDict …)`,
one `pystr_eq` gate per compound-guard conjunct, innermost the `get_field` add — with a
structural `size`-variant + `writes {written}` frame, no axiom, both provers. If this
regresses, the nested-field / compound-`and`-guard matcher or the child-projection
lowering broke.
"""
from typing import Any, Set


#@ requires True
#@ ensures True
#@ assigns written
def collect_written(node: Any, written: Set[str]) -> None:
    if isinstance(node, dict):
        if node.get("stmt") == "ArraySet":
            arr = node.get("array")
            if (isinstance(arr, dict) and arr.get("type") == "FieldGet"
                    and arr.get("object") == "self"):
                written.add(arr.get("field"))
        for v in node.values():
            collect_written(v, written)
    elif isinstance(node, list):
        for x in node:
            collect_written(x, written)
