r"""Test 9310 -- R1 CONTROL (expected PASS at HEAD; REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR at base): ast.Constant (lowered `is_constant` under the const-reflect model) and ast.Subscript tested on the same `"ExprIR"` receiver, the `_union_arm_tag` shape: R1 admits ast.Constant on this receiver (only its `.kind` stays refused), so `elt.value.id` read under the Subscript test lowers to `name_of (svalue_of elt)` and the honest two-sided bound proves; CPython agrees ([1, 0, 0, 0, 1, 0])
"""
# pycsl-expected: PASS
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
