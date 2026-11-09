# R1 REFUSE: the residual `.kind` narrowing through a BACKWARD alias (#574): `c = elt`, the test on `c`,
# the read on `elt`. CPython: 1 under `ensures \result == 0`.
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, elt: "ExprIR") -> int:
        c = elt
        if isinstance(c, ast.Constant) and isinstance(c.value, (int, float)):
            if elt.kind == "Number":
                return 0
            return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.parse("5", mode="eval").body)
    print("VIOLATION contract" if r != 0 else "result", r)
