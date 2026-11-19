# R1 REFUSE: the residual on a container element tested through a subscript. CPython: 1.
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, elt: "ExprIR") -> int:
        xs = [elt]
        if isinstance(xs[0], ast.Constant) and isinstance(elt.value, (int, float)):
            if xs[0].kind == "Number":
                return 0
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("5", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
