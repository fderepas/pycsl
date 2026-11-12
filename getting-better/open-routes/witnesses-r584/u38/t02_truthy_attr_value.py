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
