# R1 REFUSE (unchanged rule): without the const-reflect model (no `isinstance(_.value, (int, float))`
# in the file) `isinstance(elt, ast.Constant)` is not a discriminant, so it narrows as before.
# CPython: Constant(5) -> 1 under `ensures \result == 0`.
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, elt: "ExprIR") -> int:
        if isinstance(elt, ast.Constant):
            if elt.kind == "Number":
                return 0
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("5", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
