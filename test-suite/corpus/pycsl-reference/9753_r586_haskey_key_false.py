r"""Test 9753 -- route #586 WITNESS (expected FAIL: the claim is FALSE of the program): `.key` of a `HasKey` node reads its key child, not IrBinOp's `right_of`. Before run #7 (executor u43) the read was a placeholder or another class's projector and the claim PROVED; CPython breaks it.
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
        if x.kind == "HasKey":
            if x.key.kind == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(NS(kind="HasKey", dict=NS(kind="Var", name="a"), key=NS(kind="Var", name="a")))
    print("VIOLATION contract" if r != 0 else "result", r)
