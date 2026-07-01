"""todict-reflection-witnesses.py — todict-reflection-plan.md.

The emitter's `.to_dict().get(key)` IR-reflection dissolves into TYPED field
access on the (Phase-A/B) typed node: `node.to_dict().get("type") == "Var"` is
`node.kind == "Var"`. This witness verifies the typed-access TARGET the recognizer
produces — including the str-field comparison that now routes to `str_eq_op` (the
landed no-more-int step). No heterogeneous `Dict[str, Any]` model is needed.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/todict-reflection-witnesses.py
"""
from dataclasses import dataclass


@dataclass
class Node:
    kind: str

# `node.to_dict().get("type") == "Var"`  ==>  `n.kind == "Var"` (str_eq_op, not int-hash).
#@ ensures True
def is_var(n: Node) -> int:
    if n.kind == "Var":
        return 1
    return 0
