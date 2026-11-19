# R1 REFUSE: inside `_const_int_value` ast.UnaryOp IS admitted, but its `.op` stays in the residual:
# `v.op == ""` is a projector read (not an isinstance subject). CPython: -x -> 0 under `ensures \result == 1`.
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 1
    #@ assigns \nothing
    def _const_int_value(self, v: "ExprIR") -> int:
        if isinstance(v, ast.UnaryOp) and isinstance(v.op, ast.USub):
            if v.op == "":
                return 1
            return 0
        return 1


if __name__ == "__main__":
    r = Em()._const_int_value(ast.parse("-x", mode="eval").body)
    print("VIOLATION contract" if r != 1 else "result", r)
