r"""Test 9199 -- route #574 (control, expected PASS at base and HEAD): a backward alias tested against an IR class (`ast.Name`, modelled by the isinstance recognizer) is not a narrowing away from the IR model, so `node.id` keeps `name_of` and the honest claim proves
"""
# pycsl-expected: PASS
import ast
from typing import Any, Dict

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 1
    #@ assigns \nothing
    def is_x(self, node: "ExprIR") -> int:
        dv = node
        if isinstance(dv, ast.Name):
            if node.id == "x":
                return 1
        return 0
