# R1 ACCEPT: ast.Constant (is_constant under the const-reflect model, enabled by `is_num`'s
# `isinstance(elt.value, (int, float))`) and ast.Subscript tested on the same receiver (the
# `_union_arm_tag` shape): `elt.value.id` is read only under the Subscript test.
# CPython: List[int] -> 1, None -> 0, Name -> 0; `ensures 0 <= \result <= 1` holds.
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 1
    #@ assigns \nothing
    def is_num(self, elt: "ExprIR") -> int:
        if isinstance(elt, ast.Constant) and isinstance(elt.value, (int, float)):
            return 1
        return 0

    #@ ensures \result >= 0
    #@ ensures \result <= 1
    #@ assigns \nothing
    def is_list_sub(self, elt: "ExprIR") -> int:
        if isinstance(elt, ast.Constant):
            return 0
        if isinstance(elt, ast.Subscript) and isinstance(elt.value, ast.Name):
            if elt.value.id == "List":
                return 1
        return 0


if __name__ == "__main__":
    e = Em()
    rs = [e.is_list_sub(ast.parse(s, mode="eval").body) for s in ("List[int]", "None", "x", "Dict[a, b]")]
    rs += [e.is_num(ast.parse(s, mode="eval").body) for s in ("5", "x")]
    print("VIOLATION" if any(r < 0 or r > 1 for r in rs) else "result", rs)
