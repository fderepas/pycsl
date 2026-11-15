r"""Test 9758 -- route #586 WITNESS (expected FAIL: the claim is FALSE of the program): `.lo` of an `IsSorted` node reads its lower bound child. Before run #7 (executor u43) the read was a placeholder or another class's projector and the claim PROVED; CPython breaks it.
"""
# pycsl-expected: FAIL
from types import SimpleNamespace as NS

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.kind == "IsSorted":
            if x.lo.kind == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(NS(kind="IsSorted", base="a", lo=NS(kind="Var", name="i"), hi=NS(kind="Var", name="j")))
    print("VIOLATION contract" if r != 0 else "result", r)
