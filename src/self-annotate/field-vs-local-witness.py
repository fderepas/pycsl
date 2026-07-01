"""field-vs-local-witness.py — typed-ir-for-b-ceiling.md §18 (field-vs-local collision).

A record field whose name ALSO names a local var in some method collided in Why3
(`stmt.ghost_type` resolved to the local `ghost_type` ref, "cannot be applied"). The
field label is now qualified (`<record>_<field>`) in both decl and access when it
collides with a local, so `n.tag` reads the FIELD even though a local `tag` exists.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/field-vs-local-witness.py
"""
from dataclasses import dataclass
def mutable_state(cls): return cls


@dataclass
class Node:
    tag: str


@mutable_state
@dataclass
class Emitter:
    counter: int

    #@ ensures True
    def classify(self, n: Node) -> int:
        tag = "x"              # a LOCAL named `tag` — same as Node.tag
        if n.tag == "Var":     # must read the FIELD, not the local `tag`
            return 1
        return 0 if tag == "" else 2
