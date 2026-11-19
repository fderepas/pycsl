from dataclasses import dataclass
from typing import Any, Dict, List

def mutable_state(cls): return cls

@dataclass
class DictView:
    coll: str
    kind: str

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def is_keys_view(self, node: "ExprIR") -> int:
        if isinstance(dv := node, DictView):
            if dv.kind == "keys":
                return 1
        return 0
