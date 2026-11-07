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
    def is_keys_view(self, node: "ExprIR", other: "ExprIR", c: int) -> int:
        dv = node if c > 0 else other
        if isinstance(dv, DictView):
            if node.kind == "keys":
                return 1
        return 0
