"""self-ir-comp-witness.py — self-ir-schema.md IR1-IR3.

`self.ir.get("shared_vars", [])` is the typed slice `(ir_shared_vars self.ir) : array
sharedvar`; the comprehension `[sv["name"] for sv in … if sv.get("mutex")==m]` binds an
`array string` (the loop var is typed `sharedvar`, `sv["name"]` is its string field). Only
the element TYPE is modelled; content stays opaque. @mutable_state-only.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/self-ir-comp-witness.py
"""
from dataclasses import dataclass
from typing import List
def mutable_state(cls): return cls
def whyml_ident(s: str) -> str:
    #@ ensures True
    return s


@mutable_state
@dataclass
class Emitter:
    ir: int = 0            # opaque Dict[str, Any] input IR

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def shared(self, mutex: str) -> str:
        xs = [sv["name"] for sv in self.ir.get("shared_vars", []) if sv.get("mutex") == mutex]
        if xs:                     # array truthiness
            return whyml_ident(xs[0])   # index -> string
        return ""
