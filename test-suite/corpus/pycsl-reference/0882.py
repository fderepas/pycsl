"""Test 0882 — bigger-build A-unit GenericFold IN-TUPLE pre-action grammar (POSITIVE).

Exercises the generic `Dict[str, Any]` walk recognizer's IN-TUPLE + `isinstance(str)`
pre-action shape (the grammar delta landed with `_collect_assign_targets`): a
self-recursive walk that descends a heterogeneous IR dict and adds a string field to
a by-ref `Set[str]` accumulator when the node's `stmt` kind is in a literal tuple.

Lowers to the certified `pydict` catamorphism — `walk`/`walk_dict`/`walk_list` with a
structural `size`-variant (termination) + a `writes {acc}` frame — proved with NO
axiom on both provers. Type-safety + frame only (the weak self-annotation contract).
If this regresses, the in-tuple/`isinstance(str)` pre-action matcher, the by-ref set
framing, or the `size`-decrease lemma pack broke.
"""
from typing import Any, Set


#@ requires True
#@ ensures True
#@ assigns acc
def collect_assign_targets(node: Any, acc: Set[str]) -> None:
    if isinstance(node, dict):
        if node.get("stmt") in ("Assign", "AugAssign") and isinstance(node.get("target"), str):
            acc.add(node["target"])
        for v in node.values():
            collect_assign_targets(v, acc)
    elif isinstance(node, list):
        for x in node:
            collect_assign_targets(x, acc)
