r"""Test 9770 -- route #588 WITNESS (expected FAIL: the claim is FALSE of the program): the truthiness of a LOCAL bound to `.get("value")` is undecided. Before run #7 (executor u43) the read was a placeholder or another class's projector and the claim PROVED; CPython breaks it.
"""
# pycsl-expected: FAIL
from types import SimpleNamespace as NS

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 1
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        v = x.get("value")
        if v:
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f({"type": "Var", "name": "a"})
    print("VIOLATION contract" if r != 1 else "result", r)
