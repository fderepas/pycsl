# f1: dv.kind misprojection. CPython: Em().is_keys_view(DictView("d", "keys")) == 1,
# so `ensures \result == 0` is FALSE of the program. If Why3 proves it, the lowering is unsound.
from dataclasses import dataclass
from typing import Any, Dict

def mutable_state(cls): return cls

@dataclass
class DictView:
    coll: str
    kind: str

@mutable_state
class Em:
    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def is_keys_view(self, node: "ExprIR") -> int:
        if isinstance(node, DictView):
            dv = node
            if dv.kind == "keys":
                return 1
        return 0
