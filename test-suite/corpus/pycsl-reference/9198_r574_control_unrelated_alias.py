r"""Test 9198 -- route #574 (control, expected PASS at base and HEAD): the tested alias `dv = other` is NOT in `node`'s alias class, so `node.kind` keeps the emit_ir tag projection and its honest claim proves
"""
# pycsl-expected: PASS
from dataclasses import dataclass
from typing import Any, Dict

def mutable_state(cls): return cls

@dataclass
class DictView:
    coll: str
    kind: str

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 1
    #@ assigns \nothing
    def is_var(self, node: "ExprIR", other: "ExprIR") -> int:
        dv = other
        if isinstance(dv, DictView):
            return 0
        if node.kind == "Var":
            return 1
        return 0
