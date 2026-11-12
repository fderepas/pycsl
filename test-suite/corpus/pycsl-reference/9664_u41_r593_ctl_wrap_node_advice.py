r"""Test 9664 -- route #593 CONTROL, R593's advice followed: the node is WRAPPED in a class of this file (`class B: def __init__(self, node): self.node = node`) instead of subclassed; the disjoint narrowing proves `\result == 0` (expected PASS: PROVED at base 4e6004f3b and at HEAD)
"""
# pycsl-expected: PASS
from typing import Any

import ast

def mutable_state(cls): return cls


class B:
    def __init__(self, node: Any) -> None:
        self.node = node


@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Name) and isinstance(x, ast.Call):
            return 1
        return 0


if __name__ == "__main__":
    try:
        r = Em().f(B(ast.Name("a")).node)
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
