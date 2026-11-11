# R1 ACCEPT: `for elt in inner.elts` + `isinstance(elt, ast.Constant)` (the `_m5_get_type_name_legacy`
# shape: the residual `.kind` set crosses the for-edge both ways without widening), `elt.id` read
# under `isinstance(elt, ast.Name)`. CPython: Tuple(None, x) -> 1, Tuple(None) -> 0.
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 1
    #@ assigns \nothing
    def has_named(self, inner: "ExprIR") -> int:
        if isinstance(inner, ast.Tuple):
            for elt in inner.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, (int, float)):
                    continue
                if isinstance(elt, ast.Name) and elt.id != "None":
                    return 1
        return 0


if __name__ == "__main__":
    e = Em()
    rs = [e.has_named(ast.parse(s, mode="eval").body) for s in ("(1, x)", "(1, 2)", "(None,)", "y")]
    print("VIOLATION" if any(r < 0 or r > 1 for r in rs) else "result", rs)
