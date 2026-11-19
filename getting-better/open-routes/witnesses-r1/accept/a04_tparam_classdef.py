# R1 ACCEPT: a `TParamNode` parameter tested `isinstance(node, ast.ClassDef)` (is_classdef_of), its
# `.bases` elements read as emit_ir nodes (the `_collect_type_params` shape, #574's two-way closure
# over the `for` edge). CPython: class C(Generic[T]) -> 1, class D(B) -> 0.
from __future__ import annotations
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ ensures \result <= 1
    #@ assigns \nothing
    def is_generic(self, node: TParamNode) -> int:
        if isinstance(node, ast.ClassDef):
            for b in node.bases:
                if (isinstance(b, ast.Subscript) and isinstance(b.value, ast.Name)
                        and b.value.id == "Generic"):
                    return 1
        return 0


if __name__ == "__main__":
    e = Em()
    rs = [e.is_generic(ast.parse(s).body[0]) for s in ("class C(Generic[T]): pass", "class D(B): pass")]
    print("VIOLATION" if any(r < 0 or r > 1 for r in rs) else "result", rs)
