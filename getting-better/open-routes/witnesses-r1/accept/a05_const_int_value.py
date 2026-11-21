# R1 ACCEPT: the `_const_int_value` shape: `isinstance(value, ast.UnaryOp)` (is_unaryop) and the
# operator tested ONLY as the subject of `isinstance(value.op, ast.USub)` (lowered over the object,
# `str_eq_op (unaryop_op_of value) "-"`). CPython: -3 -> 1, 3 -> 0, +3 -> 0.
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 1
    #@ assigns \nothing
    def _const_int_value(self, value: "ExprIR") -> int:
        if (isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.USub)
                and isinstance(value.operand, ast.Constant)):
            return 1
        return 0


if __name__ == "__main__":
    e = Em()
    rs = [e._const_int_value(ast.parse(s, mode="eval").body) for s in ("-3", "3", "+3", "-x")]
    print("VIOLATION" if any(r < 0 or r > 1 for r in rs) else "result", rs)
