r"""Test 9773 -- route #586 WITNESS (expected FAIL: the claim is FALSE of the program): `.size` of a `GhostMake` node reads its size child, not IrBinOp's `left_of`. Before run #7 (executor u43) the read was a placeholder or another class's projector and the claim PROVED; CPython breaks it.
"""
# pycsl-expected: FAIL
from types import SimpleNamespace as NS

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.kind == "GhostMake":
            if x.size.kind == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(NS(kind="GhostMake", size=NS(kind="Var", name="n"), default=NS(kind="Number", value=0)))
    print("VIOLATION contract" if r != 0 else "result", r)
