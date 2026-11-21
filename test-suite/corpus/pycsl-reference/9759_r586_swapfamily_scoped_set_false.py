r"""Test 9759 -- route #586 WITNESS (expected FAIL: the claim is FALSE of the program): inside a method named like the swap-family handler, `.set` of a `SetMem` node reads its set child (not the scoped `left_of` slot). Before run #7 (executor u43) the read was a placeholder or another class's projector and the claim PROVED; CPython breaks it.
"""
# pycsl-expected: FAIL
from types import SimpleNamespace as NS

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def _handle_set_add_expr(self, x: "ExprIR") -> int:
        if x.kind == "SetMem":
            if x.set.kind == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em()._handle_set_add_expr(NS(kind="SetMem", elem=NS(kind="Var", name="e"), set=NS(kind="Var", name="s")))
    print("VIOLATION contract" if r != 0 else "result", r)
