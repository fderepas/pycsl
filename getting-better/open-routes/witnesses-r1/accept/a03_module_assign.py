# R1 ACCEPT: a module-body `pyast_stmt` loop local tested `isinstance(stmt, ast.Assign)` (is_assign_node),
# its `.value` (an ast.expr, `stmt_value`) then read as an emit_ir node (the `_collect_typevar_registry`
# shape). CPython: two TypeVar assigns -> 2.
import ast

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result >= 0
    #@ assigns \nothing
    def count_typevars(self, node: ast.Module) -> int:
        n = 0
        for stmt in node.body:
            if not isinstance(stmt, ast.Assign):
                continue
            call = stmt.value
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
                continue
            if call.func.id == "TypeVar":
                n = n + 1
        return n


if __name__ == "__main__":
    r = Em().count_typevars(ast.parse("T = TypeVar('T')\nU = TypeVar('U')\nx = f(1)\n"))
    print("VIOLATION" if r < 0 else "result", r)
