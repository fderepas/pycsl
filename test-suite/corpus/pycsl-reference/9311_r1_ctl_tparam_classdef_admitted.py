r"""Test 9311 -- R1 CONTROL (expected PASS at HEAD; REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR at base): `isinstance(node, ast.ClassDef)` on a `TParamNode` parameter (lowered `is_classdef_of node`), its `.bases` elements read as emit_ir nodes (the `_collect_type_params` shape through #574's two-way closure over the `for` edge); the honest bound proves; CPython agrees ([1, 0])
"""
# pycsl-expected: PASS
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
