import ast
from types import SimpleNamespace as NS

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.kind == "FieldGet":
            if x.object.kind == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(NS(kind="FieldGet", object=NS(kind="Var", name="a"), field="f"))
    print("VIOLATION contract" if r != 0 else "result", r)
