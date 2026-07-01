"""todict-varsubst-witness.py — R1 var-substitution (todict-reflection-plan.md).

`d = node.to_dict()` binds `d` as a FULL alias of the typed node, so a bare `d`
reference (passing it to a function — the emitter's `self._expr_to_whyml(d)`
recursive sub-expression emission) lowers to the node itself, not the opaque
`unit` to_dict. Complements the `d.get(key)` routing.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/todict-varsubst-witness.py
"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Node:
    kind: str

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.kind}


def emit(x: Node) -> str:
    return "e"


# `d = n.to_dict(); emit(d)`  ==>  `emit(n)` (d substitutes to the typed node).
#@ ensures True
def h(n: Node) -> str:
    d = n.to_dict()
    return emit(d)
