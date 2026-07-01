"""todict-r1-witnesses.py — todict-reflection-plan.md R1 (the reflection recognizer).

`d = node.to_dict(); d.get(key)` dissolves into TYPED field access: `d` is tracked
as an alias of the node, `d.get("type")` routes to `node.kind`, any other key to
`node.<key>`. No heterogeneous dict is materialized. Verifies end-to-end (routing +
str-eq on the typed field).

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/todict-r1-witnesses.py
"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Node:
    kind: str
    name: str

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.kind, "name": self.name}


# `d = n.to_dict(); d.get("type") == "Var"`  ==>  `n.kind == "Var"` (str_eq_op).
#@ ensures True
def classify(n: Node) -> int:
    d = n.to_dict()
    if d.get("type") == "Var":
        return 1
    if d.get("type") == "Const":
        return 2
    return 0
