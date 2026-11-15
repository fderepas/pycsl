r"""Test 9755 -- route #586 WITNESS (expected FAIL: the claim is FALSE of the program): `.left` of a `StrConcat` node reads its left child. Before run #7 (executor u43) the read was a placeholder or another class's projector and the claim PROVED; CPython breaks it.
"""
# pycsl-expected: FAIL
import ast
from types import SimpleNamespace as NS

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.kind == "StrConcat":
            if x.left.kind == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(NS(kind="StrConcat", left=NS(kind="Var", name="a"), right=NS(kind="Var", name="a")))
    print("VIOLATION contract" if r != 0 else "result", r)
