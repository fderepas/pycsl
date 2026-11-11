r"""Test 9554 -- route #584 WITNESS (expected FAIL: the claim is FALSE of the program): `x["value"]` of a `Starred` node reads its value; at base this read was `IrOther ""` on this constructor and the false `\result` claim PROVED. CPython breaks the claim.
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
        if x["type"] == "Starred":
            v = x["value"]
            if v["type"] == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f({"type": "Starred", "value": {"type": "Var", "name": "a"}})
    print("VIOLATION contract" if r != 0 else "result", r)
