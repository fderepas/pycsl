r"""Test 9564 -- route #585 WITNESS (expected FAIL: the claim is FALSE of the program): `.upper` of a node tested `Slice` reads the upper bound; at base this read was `IrOther ""` on this constructor and the false `\result` claim PROVED. CPython breaks the claim.
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
        if x.kind == "Slice":
            if x.upper.kind == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(NS(kind="Slice", lower=NS(kind="Var", name="a"), upper=NS(kind="Var", name="a")))
    print("VIOLATION contract" if r != 0 else "result", r)
