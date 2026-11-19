r"""Test 9565 -- route #585 WITNESS (expected FAIL: the claim is FALSE of the program): `.lower` of an `ast.Slice` reads the lower bound; at base this read was `IrOther ""` on this constructor and the false `\result` claim PROVED. CPython breaks the claim.
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
        if isinstance(x, ast.Slice) and isinstance(x.lower, ast.Name):
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("a[b:c]", mode="eval").body.slice)
    print("VIOLATION contract" if r != 0 else "result", r)
