r"""Test 9279 -- route #579 CONTROL (expected PASS at base 822621340 and HEAD): the standard-library `ast` bound only by `import ast` is RESOLVED even in a file that also defines a class named `CSLFieldAccess`: `isinstance(node, ast.Name)` keeps the `is_var` recognizer and `node.id` its `name_of` projector, so two reads of `node.id` are one value and the claim proves
"""
# pycsl-expected: PASS
import ast
from dataclasses import dataclass
from typing import Any

def mutable_state(cls): return cls

@dataclass
class CSLFieldAccess:
    obj: str
    kind: str

@mutable_state
class Em:
    #@ ensures \result == 1
    #@ assigns \nothing
    def same_id(self, node: "ExprIR") -> int:
        if isinstance(node, ast.Name):
            a = node.id
            b = node.id
            if a == b:
                return 1
            return 2
        return 1
