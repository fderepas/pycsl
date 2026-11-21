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
        r = 0
        for dv in [node]:
            if isinstance(dv, DictView):
                r = 1
        if r == 1:
            if node.kind == "keys":
                return 1
        return 0
