r"""Test 9325 -- R1 RED TEAM (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR at base and HEAD, every model): the receiver's name has TWO bindings (`stmt = x`, an emit_ir value, then the module-body loop target): the test `isinstance(stmt, ast.ClassDef)` on the FIRST binding is not a pyast_stmt discriminant, so it still narrows `stmt` (and `saved`) -- a read judged inside the loop (where `stmt` IS a pyast_stmt local) must not drop it. CPython: x = ClassDef "C", one module stmt -> 1 under `ensures \result == 0`.
"""
# pycsl-expected: FAIL
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, node: ast.Module, x: "ExprIR") -> int:
        stmt = x
        saved = x
        if isinstance(stmt, ast.ClassDef):
            saved = stmt
        n = 0
        for stmt in node.body:
            if isinstance(stmt, ast.ClassDef) and saved.name == "C":
                n = 1
        return n


if __name__ == "__main__":
    r = Em().f(ast.parse("class D: pass"), ast.parse("class C: pass").body[0])
    print("VIOLATION contract" if r != 0 else "result", r)
