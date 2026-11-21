r"""Test 9663 -- route #593 CONTROL: `import ast` resolved, classes with the admitted bases (`ast.NodeVisitor`, the builtin `Exception`, a class of this file); the disjoint narrowing `isinstance(x, ast.Name) and isinstance(x, ast.Call)` is infeasible, so `ensures \result == 0` needs the IR model, not a tail return (expected PASS: PROVED at base 4e6004f3b and at HEAD)
"""
# pycsl-expected: PASS
from typing import Any

import ast

def mutable_state(cls): return cls


class V(ast.NodeVisitor):
    pass


class E(Exception):
    pass


class P:
    pass


class Q(P):
    pass


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
        r = Em().f(ast.Name("a"))
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
