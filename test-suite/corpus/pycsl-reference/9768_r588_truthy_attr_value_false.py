r"""Test 9768 -- route #588 WITNESS (expected FAIL: the claim is FALSE of the program): the truthiness of `.value` on a node that carries no value is undecided. Before run #7 (executor u43) the read was a placeholder or another class's projector and the claim PROVED; CPython breaks it.
"""
# pycsl-expected: FAIL
import ast
from types import SimpleNamespace as NS

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 1
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.value:
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(NS(kind="Var", value=None))
    print("VIOLATION contract" if r != 1 else "result", r)
