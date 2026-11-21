r"""Test 9430 -- route #583 WITNESS (expected FAIL: the claim is FALSE of the program): the route exemplar: after `isinstance(x, ast.Attribute)`, `isinstance(x.value, ast.Name)` and `x.value.id == "self"` read the OBJECT (`avalue_of`), so the branch is live and the false `\result == 0` is NOT proved; at base `.value` read the Subscript projector (`IrOther ""` on an IrAttr) and the claim PROVED. CPython: `self.a` -> 1.
"""
# pycsl-expected: FAIL
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name):
            if x.value.id == "self":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("self.a", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
