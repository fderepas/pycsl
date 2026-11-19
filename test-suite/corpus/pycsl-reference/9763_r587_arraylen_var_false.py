r"""Test 9763 -- route #587 WITNESS (expected FAIL: the claim is FALSE of the program): `.var` of an `ArrayLen` node reads its array name. Before run #7 (executor u43) the read was a placeholder or another class's projector and the claim PROVED; CPython breaks it.
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
        if x.kind == "ArrayLen":
            if x.var == "a":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(NS(kind="ArrayLen", var="a"))
    print("VIOLATION contract" if r != 0 else "result", r)
