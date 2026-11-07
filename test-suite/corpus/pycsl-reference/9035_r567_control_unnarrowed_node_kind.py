r"""Test 9035 -- route #567 (control, expected PASS at base and HEAD): `node.kind` on an "ExprIR" value that NO isinstance narrows keeps the emit_ir tag projection (`kind_of`) and its honest claim proves
"""
# pycsl-expected: PASS
from typing import Any, Dict

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 1
    #@ assigns \nothing
    def is_var(self, node: "ExprIR") -> int:
        if node.kind == "Var":
            return 1
        return 0
