# R1 REFUSE (unchanged rule): ast.UnaryOp outside the `_const_int_value` arm is not a discriminant;
# `v.op` (an operator object) read by `op_of` ("" on a unary node). CPython: -x -> 0 under
# `ensures \result == 1`.
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 1
    #@ assigns \nothing
    def f(self, v: "ExprIR") -> int:
        if isinstance(v, ast.UnaryOp):
            if v.op == "":
                return 1
            return 0
        return 1


if __name__ == "__main__":
    r = Em().f(ast.parse("-x", mode="eval").body)
    print("VIOLATION contract" if r != 1 else "result", r)
