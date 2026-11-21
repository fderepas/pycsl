r"""Test 9757 -- route #586 WITNESS (expected FAIL: the claim is FALSE of the program): the dict view `.get("index", {})` of an `Nth` node reads its index child, not the Subscript `sindex_of`. Before run #7 (executor u43) the read was a placeholder or another class's projector and the claim PROVED; CPython breaks it.
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
        if x.get("type") == "Nth":
            i = x.get("index", {})
            if i.get("type") == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f({"type": "Nth", "list": {"type": "Var", "name": "a"}, "index": {"type": "Var", "name": "a"}})
    print("VIOLATION contract" if r != 0 else "result", r)
