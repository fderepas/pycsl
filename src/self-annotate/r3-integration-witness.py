"""r3-integration-witness.py — R3 (todict-reflection-plan.md): R1 + A3 COMPOSE.

A single un-\trusted, reflecting AND state-mutating handler verifies with a CHECKED
composed frame — the integration of every piece of the body-faithful-emitter arc:
  - typed IR params (B1);
  - IR-dict reflection dissolved to typed access (R1): `d = stmt.to_dict();
    d.get("type") == "Var"` -> `str_eq_op stmt.kind "Var"`; `d.get("target")` -> `stmt.target`;
  - transpiler-state mutation framed (A3): `self.dict_locals.add(...)` -> a real map
    write; `self.add_abstract_op(...)` inherited; `writes { self.dict_locals, self.abstract_ops }` CHECKED.
No trust; the frame is proven (a wrong assigns FAILS).

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/r3-integration-witness.py
"""
from dataclasses import dataclass
from typing import Set, Dict, Any
def mutable_state(cls): return cls

@dataclass
class Stmt:
    kind: str
    target: str
    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.kind, "target": self.target}

@mutable_state
@dataclass
class Emitter:
    dict_locals: Set[str]
    abstract_ops: Set[str]

    #@ assigns self.abstract_ops
    def add_abstract_op(self, op: str) -> None:
        self.abstract_ops.add(op)

    # A reflecting + mutating handler: reflects on the IR dict (R1) AND mutates
    # transpiler state (A3), with the composed assigns frame — the R3 shape.
    #@ assigns self.dict_locals, self.abstract_ops
    def handle(self, stmt: Stmt) -> str:
        d = stmt.to_dict()
        if d.get("type") == "Var":
            self.dict_locals.add(d.get("target"))
            self.add_abstract_op("val getattr_x : int")
            return "var"
        return "other"
